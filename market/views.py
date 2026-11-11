import hashlib
import json
import math
import re
from datetime import date, datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Profile, Job, Application, Dispute, AuditEvent, LoginAttempt

class Invalid(Exception): pass

def require(condition, message):
    if not condition: raise Invalid(message)

def string(data,key,maximum=300,required=True):
    value=data.get(key,'')
    require(isinstance(value,str),'Invalid text field.')
    value=value.strip()
    require((bool(value) or not required) and len(value)<=maximum, f'Please check {key} (maximum {maximum} characters).')
    return value

def public_profile(user):
    p=user.profile
    ratings=Application.objects.filter(worker=user,status='completed') if p.role=='worker' else Application.objects.filter(job__employer=user,status='completed')
    values=[(a.worker_rating if p.role=='worker' else a.employer_rating) for a in ratings]
    values=[v for v in values if v]
    return {'id':user.pk,'name':user.first_name,'role':p.role,'business':p.business,'bio':p.bio,'skills':p.skills,'completed':ratings.count(),'rating':round(sum(values)/len(values),1) if values else None,'phone_verified':p.phone_verified}

def distance(a,b,c,d):
    x,y=math.radians(c-a),math.radians(d-b)
    return round(6371*2*math.asin(min(1,math.sqrt(math.sin(x/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(y/2)**2))),1)

def job_json(j,lat=7.0873,lng=79.999):
    return {'id':j.pk,'title':j.title,'description':j.description,'category':j.category,'location':j.location,'date':str(j.date),'start':str(j.start)[:5],'end':str(j.end)[:5],'pay':j.pay,'benefits':j.benefits,'requirements':j.requirements,'status':j.status,'example':j.is_example,'distance':distance(lat,lng,j.lat,j.lng),'employer':public_profile(j.employer)}

def application_json(a,viewer):
    result={'id':a.pk,'job':job_json(a.job),'worker':public_profile(a.worker),'status':a.status,'note':a.note,'work_done':a.work_done,'payment_received':a.payment_received,'worker_rating':a.worker_rating,'employer_rating':a.employer_rating}
    if a.status in ['accepted','completed']:
        result['contact']=a.worker.profile.phone if viewer.pk==a.job.employer_id else a.job.employer.profile.phone
    return result

@ensure_csrf_cookie
def index(request): return render(request,'index.html')

def api(request,action):
    try:
        if request.method=='GET':
            if action=='state':
                me=public_profile(request.user) if request.user.is_authenticated and hasattr(request.user,'profile') else None
                if me: me['phone']=request.user.profile.phone
                return JsonResponse({'user':me,'staff':request.user.is_authenticated and request.user.is_staff,'mode':'local','integrations':{'sms':False,'whatsapp':False,'payments':False}})
            if action=='jobs':
                lat=float(request.GET.get('lat',7.0873));lng=float(request.GET.get('lng',79.999));radius=float(request.GET.get('radius',15))
                require(all(math.isfinite(v) for v in [lat,lng,radius]) and -90<=lat<=90 and -180<=lng<=180 and 1<=radius<=50,'Invalid location or radius.')
                jobs=Job.objects.filter(status='open',date__gte=timezone.localdate()).select_related('employer__profile').order_by('-created')
                q=request.GET.get('q','').strip()[:100];cat=request.GET.get('category','')
                if q: jobs=jobs.filter(title__icontains=q) | jobs.filter(description__icontains=q)
                if cat: jobs=jobs.filter(category=cat)
                results=[job_json(j,lat,lng) for j in jobs[:500]]
                return JsonResponse({'jobs':sorted([j for j in results if j['distance']<=radius],key=lambda j:j['distance'])})
            require(request.user.is_authenticated,'Please sign in.')
            if action=='applications':
                p=request.user.profile
                apps=Application.objects.filter(worker=request.user) if p.role=='worker' else Application.objects.filter(job__employer=request.user)
                return JsonResponse({'applications':[application_json(a,request.user) for a in apps.select_related('job__employer__profile','worker__profile').order_by('-created')], 'jobs':[job_json(j) for j in Job.objects.filter(employer=request.user)] if p.role=='employer' else [],'disputes':list(Dispute.objects.filter(reporter=request.user).values('id','kind','detail','status','resolution','application_id'))})
            return JsonResponse({'error':'Not found'},status=404)
        if request.method!='POST': return JsonResponse({'error':'Method not allowed'},status=405)
        require(len(request.body)<=16000,'Request too large.')
        d=json.loads(request.body)
        require(isinstance(d,dict),'Invalid request.')
        if action in ['register','login']:
            # Persisted, bounded attempt counter; not based on spoofable forwarded headers.
            key=hashlib.sha256(request.META.get('REMOTE_ADDR','').encode()).hexdigest()
            attempt,_=LoginAttempt.objects.get_or_create(key=key)
            if attempt.updated<timezone.now()-timedelta(minutes=15): attempt.failures=0
            require(attempt.failures<15,'Too many attempts. Try again in 15 minutes.')
            attempt.failures+=1;attempt.save()
            phone=string(d,'phone',20)
            require(re.fullmatch(r'\+94\d{9}',phone),'Use a Sri Lankan number such as +94771234567.')
            password=string(d,'password',128)
            if action=='register':
                require(not request.user.is_authenticated,'Sign out before creating another account.')
                name=string(d,'name',100);role=string(d,'role',10)
                require(role in ['worker','employer'],'Choose worker or employer.')
                born=date.fromisoformat(string(d,'birth_date',10));today=timezone.localdate()
                age=today.year-born.year-((today.month,today.day)<(born.month,born.day))
                require(18<=age<=110,'Rakiya is currently for adults aged 18 and over.')
                user=User(username=phone,first_name=name)
                validate_password(password,user)
                with transaction.atomic():
                    user.set_password(password);user.save()
                    Profile.objects.create(user=user,phone=phone,role=role,birth_date=born,business=string(d,'business',100,False))
                login(request,user)
            else:
                user=authenticate(request,username=phone,password=password)
                require(user is not None,'Phone number or password is incorrect.')
                login(request,user)
            attempt.failures=0;attempt.save()
            return JsonResponse({'ok':True})
        require(request.user.is_authenticated,'Please sign in.')
        if action=='logout': logout(request);return JsonResponse({'ok':True})
        p=request.user.profile
        if action=='profile':
            request.user.first_name=string(d,'name',100);request.user.save(update_fields=['first_name'])
            p.bio=string(d,'bio',600,False);p.skills=string(d,'skills',250,False);p.business=string(d,'business',100,False);p.save()
        elif action=='post':
            require(p.role=='employer','Only employers can post jobs.')
            day=date.fromisoformat(string(d,'date',10));start=datetime.strptime(string(d,'start',5),'%H:%M').time();end=datetime.strptime(string(d,'end',5),'%H:%M').time()
            require(day>=timezone.localdate(),'Choose today or a future date.')
            require(end>start,'End time must follow start time. Split overnight shifts into separate listings.')
            pay=int(d.get('pay',0));lat=float(d.get('lat',7.0873));lng=float(d.get('lng',79.999))
            require(100<=pay<=1000000,'Pay must be between LKR 100 and 1,000,000.')
            require(math.isfinite(lat) and math.isfinite(lng) and distance(7.0873,79.999,lat,lng)<=20,'For this pilot, choose a location within 20 km of Gampaha town.')
            category=string(d,'category',30);require(category in ['Retail','Hospitality','Events','General'],'Choose a category.')
            Job.objects.create(employer=request.user,title=string(d,'title',100),description=string(d,'description',3000),category=category,location=string(d,'location',150),date=day,start=start,end=end,pay=pay,lat=lat,lng=lng,benefits=string(d,'benefits',200,False),requirements=string(d,'requirements',300,False))
            AuditEvent.objects.create(actor=request.user,action='post_job',target=string(d,'title',100))
        elif action=='apply':
            require(p.role=='worker','Only workers can apply.')
            with transaction.atomic():
                job=get_object_or_404(Job,pk=int(d['job']))
                require(job.status=='open' and job.date>=timezone.localdate(),'This job is no longer open.')
                require(not job.is_example,'Example listings are for browsing. Ask a test employer to post a real local-test listing.')
                Application.objects.create(job=job,worker=request.user,note=string(d,'note',600,False))
        elif action=='cancel_job':
            with transaction.atomic():
                j=get_object_or_404(Job,pk=int(d['job']),employer=request.user)
                require(j.status in ['open','filled'],'This job cannot be cancelled.')
                require(not Application.objects.filter(job=j,work_done=True).exists(),'Work is already marked done. Please use dispute reporting.')
                j.status='cancelled';j.save()
                Application.objects.filter(job=j).exclude(status__in=['completed','rejected']).update(status='cancelled')
                AuditEvent.objects.create(actor=request.user,action='cancel_job',target=str(j.pk))
        elif action in ['decision','complete','payment','withdraw','dispute']:
            with transaction.atomic():
                a=get_object_or_404(Application.objects.select_for_update().select_related('job'),pk=int(d['application']))
                owner=a.job.employer_id==request.user.pk;worker=a.worker_id==request.user.pk
                require(owner or worker,'You cannot access this application.')
                if action=='decision':
                    require(owner and a.status in ['pending','hold'] and a.job.status=='open' and a.job.date>=timezone.localdate(),'This application cannot be changed.')
                    status=string(d,'status',15);require(status in ['accepted','rejected','hold'],'Invalid decision.')
                    a.status=status
                    if status=='accepted':
                        a.job.status='filled';a.job.save()
                        Application.objects.filter(job=a.job,status__in=['pending','hold']).exclude(pk=a.pk).update(status='rejected')
                elif action=='withdraw':
                    require(worker and a.status in ['pending','hold','accepted'] and not a.work_done,'This application cannot be withdrawn.')
                    was_accepted=a.status=='accepted';a.status='cancelled'
                    if was_accepted:a.job.status='open';a.job.save()
                elif action=='complete':
                    require(owner and a.status=='accepted' and not a.work_done,'Only the hiring employer can confirm work once.')
                    require(timezone.localdate()>=a.job.date,'Work cannot be confirmed before the shift date.')
                    rating=int(d.get('rating',0));require(1<=rating<=5,'Choose a rating from 1 to 5.')
                    a.worker_rating=rating;a.work_done=True
                elif action=='payment':
                    require(worker and a.status=='accepted' and a.work_done and not a.payment_received,'The employer must confirm the work first.')
                    require(d.get('confirmed') is True,'Confirm that all agreed compensation was received.')
                    rating=int(d.get('rating',0));require(1<=rating<=5,'Choose a rating from 1 to 5.')
                    a.employer_rating=rating;a.payment_received=True
                elif action=='dispute':
                    kind=string(d,'kind',20);require(kind in ['payment','no_show','cancellation','safety','other'],'Choose a report type.')
                    require(not Dispute.objects.filter(application=a,reporter=request.user,status='open').exists(),'You already have an open report for this application.')
                    Dispute.objects.create(application=a,reporter=request.user,kind=kind,detail=string(d,'detail',2000))
                if a.work_done and a.payment_received:
                    a.status='completed';a.job.status='completed';a.job.save()
                a.save()
                AuditEvent.objects.create(actor=request.user,action=action,target=str(a.pk))
        else:return JsonResponse({'error':'Not found'},status=404)
        return JsonResponse({'ok':True})
    except (Invalid,ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        return JsonResponse({'error':str(e) if isinstance(e,Invalid) else 'Please check the submitted fields.'},status=400)
    except ValidationError as e:return JsonResponse({'error':' '.join(e.messages)},status=400)
    except IntegrityError:return JsonResponse({'error':'This phone number or application already exists, or this job has already been filled.'},status=409)
