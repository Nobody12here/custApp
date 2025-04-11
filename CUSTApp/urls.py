# CUSTApp/urls.py
from django.urls import path
from . import views
from .views import (
    DepartmentRetrieveUpdateDestroyAPI, GeneratePDFAPIView, GetAttributesAPIView, 
    GenerateLetterAPIView, UserRetrieveUpdateDestroyAPI, UsersList, DepartmentList, RequestList,
    TemplateAttributesList, RequestCreate, index_page, test_api_view, OTPSendView, OTPVerifyView, 
    verify_otp_page, admin_dashboard, user_dashboard, ApplicationRequestAPIView  # Added new view
)

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.students, name='students'),
    path('about/', views.about, name='about'),
    path('test/', test_api_view, name='test_api'),
    path('users/', UsersList.as_view(), name='users_list'),
    path('departments/', DepartmentList.as_view(), name='departments_list'),
    path('requests/', RequestList.as_view(), name='requests_list'),
    path('template-attributes/', TemplateAttributesList.as_view(), name='template_attributes_list'),
    path('requests/create/', RequestCreate.as_view(), name='request_create'),
    path('generate-letter/<int:request_id>/', GenerateLetterAPIView.as_view(), name='generate_letter'),
    path('api/request-otp/', OTPSendView.as_view(), name='otp_send'),
    path('api/verify-otp/', OTPVerifyView.as_view(), name='otp_verify'),
    path('verify_otp/', verify_otp_page, name='verify_otp_page'),
    path('index/', index_page, name='index_page'),
    path('users/<int:user_id>/', UserRetrieveUpdateDestroyAPI.as_view(), name='user_detail'),
    path('departments/<int:dept_id>/', DepartmentRetrieveUpdateDestroyAPI.as_view(), name='department_detail'),
    path('api/get_attributes/', GetAttributesAPIView.as_view(), name='get_attributes'),
    path('api/generate_pdf/', GeneratePDFAPIView.as_view(), name='generate_pdf'),
    path('myadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('myapplications/', views.view_applications, name='view_applications'),
    path('categories/', views.categories, name='categories'),
    path('new-application/', views.new_application, name='new_application'),
    path('reports/', views.reports, name='reports'),
    # New endpoint for ApplicationRequestAPIView
    # path('api/application-template/',ApplicationTemplateViewset.as_view({'get':'list'}),name='applicationTemplate_api'),
    path('api/application-request/', ApplicationRequestAPIView.as_view(), name='application_request'),
]