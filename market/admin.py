from django.contrib import admin
from .models import Profile, Job, Application, Dispute, AuditEvent

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','role','business','phone_verified']
    readonly_fields = ['phone_verified']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title','employer','date','status','is_example']
    list_filter = ['status','is_example']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['job','worker','status','payment_received','work_done']
    readonly_fields = ['job','worker','status','payment_received','work_done','worker_rating','employer_rating','note']
    def has_add_permission(self,request): return False

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['id','kind','reporter','status','created']
    list_filter = ['status','kind']
    readonly_fields = ['application','reporter','kind','detail','created']
    def has_add_permission(self,request): return False
    def save_model(self,request,obj,form,change):
        super().save_model(request,obj,form,change)
        AuditEvent.objects.create(actor=request.user,action='dispute_review',target=f'{obj.pk}:{obj.status}')

@admin.register(AuditEvent)
class AuditAdmin(admin.ModelAdmin):
    list_display = ['actor','action','target','created']
    readonly_fields = ['actor','action','target','created']
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
