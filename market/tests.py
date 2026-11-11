import json
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone
from .models import Profile, Job, Application, Dispute, LoginAttempt

class JourneyTests(TestCase):
    def setUp(self):
        self.employer=self.person('employer','+94770000001')
        self.worker=self.person('worker','+94770000002')
        self.other=self.person('worker','+94770000003')
        self.job=Job.objects.create(employer=self.employer,title='Test shift',description='Help at a shop',category='Retail',location='Gampaha',date=timezone.localdate(),start=time(9),end=time(17),pay=3000)
    def person(self,role,phone):
        u=User.objects.create_user(username=phone,password='LocalTest!82947',first_name=role)
        Profile.objects.create(user=u,role=role,phone=phone,birth_date=date(1995,1,1))
        return u
    def post(self,action,data,user=None):
        if user:self.client.force_login(user)
        return self.client.post('/api/'+action+'/',json.dumps(data),content_type='application/json')
    def apply(self):
        self.assertEqual(self.post('apply',{'job':self.job.pk},self.worker).status_code,200)
        return Application.objects.get(job=self.job)
    def accept(self):
        a=self.apply();self.assertEqual(self.post('decision',{'application':a.pk,'status':'accepted'},self.employer).status_code,200);return a
    def test_full_hiring_and_payment_journey(self):
        a=self.apply()
        data=self.client.get('/api/applications/').json()['applications'][0]
        self.assertNotIn('contact',data)
        self.assertEqual(self.post('decision',{'application':a.pk,'status':'accepted'},self.employer).status_code,200)
        data=self.client.get('/api/applications/').json()['applications'][0]
        self.assertEqual(data['contact'],self.worker.profile.phone)
        self.assertEqual(self.post('complete',{'application':a.pk,'rating':5},self.employer).status_code,200)
        self.assertEqual(self.post('payment',{'application':a.pk,'rating':4,'confirmed':True},self.worker).status_code,200)
        a.refresh_from_db();self.job.refresh_from_db()
        self.assertEqual(a.status,'completed');self.assertEqual(self.job.status,'completed')
        self.assertEqual(a.worker_rating,5);self.assertEqual(a.employer_rating,4)
    def test_contact_hidden_when_pending_and_on_hold(self):
        a=self.apply();self.post('decision',{'application':a.pk,'status':'hold'},self.employer)
        self.assertNotIn('contact',self.client.get('/api/applications/').json()['applications'][0])
    def test_unrelated_worker_cannot_read_or_change_match(self):
        a=self.accept();r=self.post('payment',{'application':a.pk,'rating':5,'confirmed':True},self.other)
        self.assertEqual(r.status_code,400)
        self.assertEqual(self.client.get('/api/applications/').json()['applications'],[])
    def test_employer_cannot_apply(self):
        self.assertEqual(self.post('apply',{'job':self.job.pk},self.employer).status_code,400)
    def test_worker_cannot_post(self):
        self.assertEqual(self.post('post',{},self.worker).status_code,400)
    def test_duplicate_application_rejected(self):
        self.apply();self.assertEqual(self.post('apply',{'job':self.job.pk},self.worker).status_code,409)
    def test_worker_cannot_accept_self(self):
        a=self.apply();self.assertEqual(self.post('decision',{'application':a.pk,'status':'accepted'},self.worker).status_code,400)
    def test_only_one_hire(self):
        a=self.apply();self.post('apply',{'job':self.job.pk},self.other)
        b=Application.objects.get(worker=self.other)
        self.post('decision',{'application':a.pk,'status':'accepted'},self.employer)
        self.assertEqual(self.post('decision',{'application':b.pk,'status':'accepted'},self.employer).status_code,400)
        b.refresh_from_db();self.assertEqual(b.status,'rejected')
    def test_payment_requires_work_and_confirmation(self):
        a=self.accept()
        self.assertEqual(self.post('payment',{'application':a.pk,'rating':5,'confirmed':True},self.worker).status_code,400)
        self.post('complete',{'application':a.pk,'rating':5},self.employer)
        self.assertEqual(self.post('payment',{'application':a.pk,'rating':5,'confirmed':False},self.worker).status_code,400)
    def test_rating_bounds(self):
        a=self.accept();self.assertEqual(self.post('complete',{'application':a.pk,'rating':6},self.employer).status_code,400)
    def test_future_shift_cannot_complete(self):
        self.job.date=timezone.localdate()+timedelta(days=1);self.job.save();a=self.accept()
        self.assertEqual(self.post('complete',{'application':a.pk,'rating':5},self.employer).status_code,400)
    def test_withdraw_removes_contact_and_reopens_job(self):
        a=self.accept();self.post('withdraw',{'application':a.pk},self.worker)
        self.job.refresh_from_db();self.assertEqual(self.job.status,'open')
        self.assertNotIn('contact',self.client.get('/api/applications/').json()['applications'][0])
    def test_cancel_job_cancels_applications(self):
        a=self.accept();self.post('cancel_job',{'job':self.job.pk},self.employer)
        a.refresh_from_db();self.assertEqual(a.status,'cancelled')
    def test_cannot_cancel_after_work_confirmed(self):
        a=self.accept();self.post('complete',{'application':a.pk,'rating':5},self.employer)
        self.assertEqual(self.post('cancel_job',{'job':self.job.pk},self.employer).status_code,400)
    def test_reports_private_and_duplicates_rejected(self):
        a=self.accept();payload={'application':a.pk,'kind':'payment','detail':'Payment missing'}
        self.assertEqual(self.post('dispute',payload,self.worker).status_code,200)
        self.assertEqual(self.post('dispute',payload,self.worker).status_code,400)
        self.client.force_login(self.other);self.assertEqual(self.client.get('/api/applications/').json()['disputes'],[])
    def test_profile_cannot_escalate_role_or_verify_phone(self):
        self.post('profile',{'name':'New Name','role':'employer','phone_verified':True},self.worker)
        self.worker.profile.refresh_from_db();self.assertEqual(self.worker.profile.role,'worker');self.assertFalse(self.worker.profile.phone_verified)
    def test_examples_not_applicable(self):
        self.job.is_example=True;self.job.save()
        self.assertEqual(self.post('apply',{'job':self.job.pk},self.worker).status_code,400)
    def test_invalid_geo_inputs_rejected(self):
        for query in ['lat=nan','radius=-1','lng=999']:
            self.assertEqual(self.client.get('/api/jobs/?'+query).status_code,400)
    def test_distance_and_date_filter(self):
        self.assertEqual(len(self.client.get('/api/jobs/?lat=7.0873&lng=79.999&radius=15').json()['jobs']),1)
        self.assertEqual(len(self.client.get('/api/jobs/?lat=6.9&lng=79.8&radius=5').json()['jobs']),0)
        self.job.date=timezone.localdate()-timedelta(days=1);self.job.save()
        self.assertEqual(self.client.get('/api/jobs/').json()['jobs'],[])
    def test_registration_adult_and_password_validation(self):
        payload={'phone':'+94771111111','password':'LocalTest!83957','name':'Test Adult','birth_date':str(timezone.localdate().replace(year=timezone.localdate().year-17)),'role':'worker'}
        self.assertEqual(self.post('register',payload).status_code,400)
        payload['birth_date']='1995-01-01';payload['password']='123'
        self.assertEqual(self.post('register',payload).status_code,400)
        payload['password']='LocalTest!83957';self.assertEqual(self.post('register',payload).status_code,200)
        u=User.objects.get(username=payload['phone']);self.assertTrue(u.check_password(payload['password']));self.assertNotEqual(u.password,payload['password'])
        self.assertFalse(u.profile.phone_verified)
    def test_post_and_listing(self):
        d={'title':'New shift','description':'Shop help','category':'Retail','location':'Town','date':str(timezone.localdate()),'start':'09:00','end':'17:00','pay':3500,'lat':7.0873,'lng':79.999}
        self.assertEqual(self.post('post',d,self.employer).status_code,200)
        self.assertEqual(len(self.client.get('/api/jobs/?q=New&category=Retail').json()['jobs']),1)
        d['end']='08:00';self.assertEqual(self.post('post',d,self.employer).status_code,400)
    def test_login_throttle_and_logout(self):
        for _ in range(15):self.post('login',{'phone':self.worker.username,'password':'IncorrectPassword'})
        self.assertEqual(self.post('login',{'phone':self.worker.username,'password':'LocalTest!82947'}).status_code,400)
        LoginAttempt.objects.all().delete()
        self.assertEqual(self.post('login',{'phone':self.worker.username,'password':'LocalTest!82947'}).status_code,200)
        self.assertEqual(self.client.cookies['sessionid']['httponly'],True)
        self.assertEqual(self.post('logout',{}).status_code,200)
        self.assertIsNone(self.client.get('/api/state/').json()['user'])
    def test_csrf_is_enforced_and_public_page_renders(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.get('/').status_code,200)
        self.assertEqual(c.post('/api/login/',json.dumps({'phone':self.worker.username,'password':'LocalTest!82947'}),content_type='application/json').status_code,403)
        token=c.cookies['csrftoken'].value
        self.assertEqual(c.post('/api/login/',json.dumps({'phone':self.worker.username,'password':'LocalTest!82947'}),content_type='application/json',HTTP_X_CSRFTOKEN=token).status_code,200)
    def test_admin_is_not_public(self):
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get('/admin/market/dispute/').status_code,302)
