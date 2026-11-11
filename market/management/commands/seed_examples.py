from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from market.models import Profile, Job

class Command(BaseCommand):
    help = 'Create fictional, browse-only jobs. No usable account password is created.'
    def handle(self,*args,**options):
        rows=[('Retail assistant','Retail','Town Centre Store','Gampaha town',3000,'Lunch included',7.0873,79.999),('Café team member','Hospitality','The Corner Café','Yakkala',3500,'Lunch + tea',7.086,80.029),('Event setup helper','Events','Neighbourhood Events','Miriswatta',4000,'Meal + travel allowance',7.065,80.008),('Shop stock assistant','Retail','Local Market Store','Bemmulla',3200,'Lunch included',7.126,80.008),('Kitchen assistant','Hospitality','Gampaha Kitchen','Gampaha town',3000,'Meals provided',7.083,79.995),('Packing assistant','General','Community Supplies','Ganemulla',2800,'Tea provided',7.06,79.964)]
        for i,(title,category,business,location,pay,benefits,lat,lng) in enumerate(rows):
            user,created=User.objects.get_or_create(username=f'example-employer-{i}',defaults={'first_name':business})
            if created:user.set_unusable_password();user.save()
            Profile.objects.get_or_create(user=user,defaults={'role':'employer','phone':'+94000000000','birth_date':date(1990,1,1),'business':business})
            Job.objects.update_or_create(employer=user,is_example=True,defaults={'title':title,'category':category,'location':location,'pay':pay,'benefits':benefits,'lat':lat,'lng':lng,'date':timezone.localdate()+timedelta(days=1+i%3),'start':time(9),'end':time(17),'description':'Fictional example for exploring Rakiya. This is not a real vacancy. Create a local-test employer account and post your own job to test applications.','requirements':'Standing and light manual work. Confirm requirements with the employer.','status':'open'})
        self.stdout.write(self.style.SUCCESS('Six fictional, browse-only listings are ready. No demo passwords or real phone numbers were created.'))
