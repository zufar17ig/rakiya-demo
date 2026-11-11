from django.conf import settings
from django.db import models
from django.db.models import Q

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('worker', 'Worker'), ('employer', 'Employer')])
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    bio = models.CharField(max_length=600, blank=True)
    skills = models.CharField(max_length=250, blank=True)
    business = models.CharField(max_length=100, blank=True)
    phone_verified = models.BooleanField(default=False)

class Job(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=3000)
    category = models.CharField(max_length=30)
    location = models.CharField(max_length=150)
    lat = models.FloatField(default=7.0873)
    lng = models.FloatField(default=79.999)
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    pay = models.PositiveIntegerField()
    benefits = models.CharField(max_length=200, blank=True)
    requirements = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=15, default='open', choices=[('open','Open'),('filled','Filled'),('completed','Completed'),('cancelled','Cancelled')])
    is_example = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(pay__gt=0), name='positive_pay')]

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.PROTECT)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.CharField(max_length=600, blank=True)
    status = models.CharField(max_length=15, default='pending', choices=[('pending','Pending'),('hold','On hold'),('accepted','Accepted'),('rejected','Rejected'),('cancelled','Cancelled'),('completed','Completed')])
    work_done = models.BooleanField(default=False)
    payment_received = models.BooleanField(default=False)
    worker_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    employer_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['job','worker'],name='one_application_per_worker'), models.UniqueConstraint(fields=['job'],condition=Q(status__in=['accepted','completed']),name='one_hire_per_job')]

class Dispute(models.Model):
    application = models.ForeignKey(Application,on_delete=models.PROTECT)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    kind = models.CharField(max_length=20, choices=[('payment','Payment'),('no_show','No show'),('cancellation','Cancellation'),('safety','Safety'),('other','Other')])
    detail = models.TextField(max_length=2000)
    status = models.CharField(max_length=12,default='open',choices=[('open','Open'),('resolved','Resolved')])
    resolution = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    target = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

class LoginAttempt(models.Model):
    key = models.CharField(max_length=64,unique=True)
    failures = models.PositiveSmallIntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
