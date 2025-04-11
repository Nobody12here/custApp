from django.contrib import admin
from .models import Users, Department, TemplateAttributes

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('uu_id', 'name', 'email', 'user_type', 'created_at')
    search_fields = ('uu_id', 'name', 'email')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_name', 'dept_head', 'short_name', 'dept_id')
    search_fields = ('dept_name',)

# @admin.register(Applications)
# class ApplicationsAdmin(admin.ModelAdmin):
#     list_display = ('application_name', 'short_name', 'status', 'responsible_dept', 'created_at')
#     list_filter = ('status', 'responsible_dept')
#     search_fields = ('application_name', 'short_name')

# @admin.register(Request)
# class RequestAdmin(admin.ModelAdmin):
#     list_display = ('request_id', 'application', 'applicant', 'status', 'created_at')
#     list_filter = ('status', 'payment_status')
#     search_fields = ('request_id', 'applicant__uu_id')

@admin.register(TemplateAttributes)
class TemplateAttributesAdmin(admin.ModelAdmin):
    list_display = ('attribute_name', 'attribute_value', 'created_at')
    search_fields = ('attribute_name',)
