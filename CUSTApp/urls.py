# CUSTApp/urls.py
from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter
from CUSTApp.views_detail.convocation_views import (
    SendConvocationEmailsAPIView,
    BulkGenerateConvocationLettersAPIView,
    GenerateConvocationLetterAPIView,
    ConvocationStudentsListView,
)
from .views import (
    AllUsersListAPIView,
    DepartmentRetrieveUpdateDestroyAPI,
    GeneratePDFWithLetterheadAPIView,
    GetAttributesAPIView,
    RequestRetrieveAPIView,
    SupportTicketAPIView,
    UserUpdateView,
    UsersList,
    DepartmentList,
    complaints,
    index_page,
    request_verification_page,
    test_api_view,
    OTPSendView,
    OTPVerifyView,
    verify_otp_page,
    ApplicationRequestAPIView,
    AluminiSignupAPIView,
    ProgramView,  # Added new view
)

router = DefaultRouter()
router.register(r"program", ProgramView)
router.register(r"convocation", views.ConvocationView, basename="convocation")
urlpatterns = [
    path("", views.home, name="home_"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("students/", views.students, name="students"),
    path("convocation-page/", views.convocation, name="convocation_page"),
    path("about/", views.about, name="about"),
    path("users/", UsersList.as_view(), name="users_list"),
    path("admin-departments/", views.admin_department, name="admin_departments"),
    path("admin-templates/", views.admin_templates, name="admin_templates"),
    path("admin-faculty/", views.admin_faculty, name="admin_faculty"),
    path("departments/", DepartmentList.as_view(), name="departments_list"),
    path("requests/", include("user_requests.urls"), name="requests_list"),
    path("request-otp/", OTPSendView.as_view(), name="otp_send"),
    path('alumini-signup/',AluminiSignupAPIView.as_view(),name="alumini_signup"),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp_verify"),
    path("otp/verifyAPI/", OTPVerifyView.as_view(), name="otp_verify"),
    path("verify_otp/", verify_otp_page, name="verify_otp_page"),
    path("index/", index_page, name="index_page"),
    path(
        "users/<int:user_id>/",
        UserUpdateView.as_view(),
        name="user_detail",
    ),
    path(
        "departments/<int:dept_id>/",
        DepartmentRetrieveUpdateDestroyAPI.as_view(),
        name="department_detail",
    ),
    path("api/get_attributes/", GetAttributesAPIView.as_view(), name="get_attributes"),
    path("myadmin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("user/dashboard/", views.user_dashboard, name="user_dashboard"),
    path("profile/", views.user_profile, name="profile"),
    path("myapplications/", views.view_applications, name="view_applications"),
    path("categories/", views.categories, name="categories"),
    path("new-application/", views.new_application, name="new_application"),
    path("reports/", views.reports, name="reports"),
    path("support/", views.support, name="support"),
    path("privacy-policy/", views.privacy_policy, name="privacy-policy"),
    path(
        "api/applications/",
        views.ApplicationListView.as_view(),
        name="application-list",
    ),
    path(
        "api/application-request/",
        ApplicationRequestAPIView.as_view(),
        name="application_request",
    ),
    path(
        "api/delete-request/<int:pk>/",
        views.RequestDelete.as_view(),
        name="delete_request",
    ),
    path(
        "update-rendered-template/<int:id>/",
        views.update_rendered_template,
        name="update_rendered_template",
    ),
    path(
        "update-request-status/<int:id>/",
        views.update_request_status,
        name="update_request_status",
    ),
    path("add-comment/<int:id>/", views.AddCommentView.as_view(), name="add_comment"),
    path(
        "generate-pdf-with-letterhead/",
        GeneratePDFWithLetterheadAPIView.as_view(),
        name="generate_pdf_with_letterhead",
    ),
    path("api/logout/", views.LogoutAPIView.as_view(), name="logout_view"),
    path(
        "api/upload-signature/",
        views.UploadEmployeeSignature.as_view(),
        name="upload-signature",
    ),
    path("guest-pass/", views.guest_pass, name="guest_pass"),
    path("public-guestpass/", views.public_guest_pass, name="public_guest_pass"),
    path(
        "public-guestpass/<int:pass_id>/",
        views.public_guest_pass,
        name="public_guest_pass",
    ),
    path("home/", views.home, name="home"),
    path(
        "api/support-ticket/", SupportTicketAPIView.as_view(), name="support_ticket_api"
    ),
    path("api/all-users/", AllUsersListAPIView.as_view(), name="all_users_list"),
    path(
        "api/requests/<int:request_id>/",
        RequestRetrieveAPIView.as_view(),
        name="request-detail",
    ),
    path(
        "verify/request/<int:request_id>/",
        request_verification_page,
        name="request-verification",
    ),
    path("complaints/", complaints, name="complaints"),
    path(
        "api/upload-convocation-data/",
        views.UploadConvocationData.as_view(),
        name="upload_convocation_data",
    ),
    path(
        "api/upload-student-data/",
        views.UploadStudentData.as_view(),
        name="upload_student_data",
    ),
    # Convocation Letter Generation APIs
    path(
        "api/generate-convocation-letter/",
        GenerateConvocationLetterAPIView.as_view(),
        name="generate_convocation_letter",
    ),
    path(
        "api/bulk-generate-convocation-letters/",
        BulkGenerateConvocationLettersAPIView.as_view(),
        name="bulk_generate_convocation_letters",
    ),
    path(
        "api/send-convocation-emails/",
        SendConvocationEmailsAPIView.as_view(),
        name="send_convocation_emails",
    ),
    path(
        "convocation/students/",
        ConvocationStudentsListView.as_view(),
        name="convocation_students_list",
    ),
]
urlpatterns.extend(router.urls)
