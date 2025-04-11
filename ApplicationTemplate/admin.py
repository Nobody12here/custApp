from django.contrib import admin
from .models import Applications,Request
# Register your models here.

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('application_name', 'short_name', 'status', 'responsible_dept', 'created_at')
    list_filter = ('status', 'responsible_dept')
    search_fields = ('application_name', 'short_name')
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'application', 'applicant', 'status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('request_id', 'applicant__uu_id')