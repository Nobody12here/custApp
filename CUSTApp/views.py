# CUSTApp/views.py
from datetime import datetime
import threading
from django.urls import reverse
import pandas as pd
import qrcode
from reportlab.platypus import Image as RLImage
import re
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from ApplicationTemplate.models import Applications, Request
from .models import Program, Users, Department, Convocation
from ApplicationTemplate.serializers import ApplicationsSerializer, RequestSerializer
from .serializers import (
    ProgramSerializer,
    UserUpdateSerializer,
    UsersSerializer,
    DepartmentSerializer,
    OTPSendSerializer,
    OTPVerifySerializer,
    PhoneOTPVerifySerializer,
    ConvocationSerializer,
)
from user_requests.serializers import ComplaintSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import (
    send_alert_email,
    add_comment_to_instance,
    notify_user_devices,
    extract_year_term,
    load_convocation_data,
    send_email_async,
    upload_student_data,
)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
import random
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ModelViewSet

import os
from PyPDF2 import PdfReader, PdfWriter

logger = logging.getLogger("custom_logger")


class ConvocationView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConvocationSerializer

    def get_queryset(self):
        queryset = Convocation.objects.all()
        return queryset


class UploadStudentData(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        student_data = request.FILES.get("student_data")
        if not student_data:
            return Response(
                {"error": "Data file not provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not student_data.name.endswith(".xlsx"):
            return Response(
                {"error": "Only .xlsx files are supported"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = upload_student_data(student_data)
            return Response(
                {
                    "message": "Student data uploaded and student records updated.",
                    "result": result,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to process file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UploadConvocationData(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]  # Will set per-method

    def post(self, request):
        convocation_id = request.data.get("convocation_id")
        convocation_file = request.FILES.get("convocation_data")
        if not convocation_file:
            return Response(
                {"error": "Data file not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not convocation_id:
            return Response(
                {"error": "Convocation ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not convocation_file.name.endswith(".xlsx"):
            return Response(
                {"error": "Only .xlsx files are supported"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # load_convocation_data should handle the file and update student data
            convocation_instance = Convocation.objects.get(id=convocation_id)
            result = load_convocation_data(convocation_file, convocation_instance)
            return Response(
                {
                    "message": "Convocation data uploaded and student records updated.",
                    "result": result,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to process file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        convocation_id = request.data.get("convocation_id")
        student_id = request.data.get("student_id")
        if not convocation_id or not student_id:
            return Response(
                {"error": "Convocation ID and Student ID required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            convocation = Convocation.objects.get(id=convocation_id)
            student = Users.objects.get(uu_id=student_id, user_type="Student")
            student.convocation = convocation
            student.save()
            return Response(
                {"message": "Updated sucessfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        student_id = request.data.get("student_id")
        if not student_id:
            return Response(
                {"error": "Student ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            student = Users.objects.get(uu_id=student_id, user_type="Student")
            student.convocation = None
            student.save()
            return Response(
                {"message": "Student deleted sucessfully!"}, status=status.HTTP_200_OK
            )
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UploadEmployeeSignature(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        user = self.request.user
        image = self.request.FILES.get("signature")
        if not image:
            return Response(
                {"error": "No image provided!"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = Users.objects.get(user_id=user.user_id)
            user.signature = image
            user.save()
            return Response(
                {"message": "Signature Uploaded sucessfully !"},
                status=status.HTTP_201_CREATED,
            )
        except ObjectDoesNotExist:
            return Response(
                {"error": " this user does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )


class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        # User info
        req = Request.objects.get(pk=id)
        student = req.applicant
        employee = Users.objects.get(user_id=req.EmployeeID)

        text = request.data.get("text")
        if not text:
            return Response(
                {"error": "Comment text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return add_comment_to_instance(request, req, student=student, employee=employee)


@csrf_exempt
def update_request_status(request, id):
    if request.method == "POST":
        status = request.POST.get("status")
        if status not in ["Approved", "Rejected", "Visited", "Resolved"]:
            return JsonResponse({"error": "Invalid status"}, status=400)
        try:
            req = Request.objects.get(pk=id)
            if req.request_type == "GuestPass":
                if (
                    request.user.user_type != "Security"
                    and req.host.user_id != request.user.user_id
                ):
                    return JsonResponse(
                        {
                            "error": "Only the host or Security department can change the status"
                        },
                        status=401,
                    )

            host = req.host
            guest = req.guest
            student = req.applicant
            req.status = status
            if status == "Visited":
                req.vistied_at = timezone.now().isoformat()
            req.approved_at = timezone.now().isoformat()
            req.save()
            user = host or student
            if guest:
                print("Sending notification to guest")
                notify_user_devices(
                    guest,
                    title="Request Update",
                    body=f"Your {req.request_type} request (ID: {req.request_id}) is now {status.lower()}. {'' if status.lower()=='rejected' else 'Please arrive early and bring your original CNIC with you.'}",
                    url="",
                )
            if user:
                send_alert_email(
                    user.email,
                    "Application Status Update",
                    f"The status of your application of {req.request_type} Type with Request ID # {req.request_id} has been updated to {status.lower()}",
                    recipient_name=user.name,
                )
            return JsonResponse({"success": True})
        except Request.DoesNotExist:
            return JsonResponse({"error": "Request not found"}, status=404)
    return JsonResponse({"error": "Invalid method"}, status=405)


def update_rendered_template(request, id):
    if request.method == "POST":
        content = request.POST.get("content")
        try:
            req = Request.objects.get(pk=id)
            req.renderedtemplate = content
            req.save()
            return JsonResponse({"success": True})
        except Request.DoesNotExist:
            return JsonResponse({"error": "Request not found"}, status=404)


class ApplicationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationsSerializer

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        if user_type == "Staff":
            return Applications.objects.filter(
                status=1, default_responsible_employee_id=user.user_id
            )
        elif user_type == "Student":
            return Applications.objects.filter(status=1)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Return only id and application_name for the dropdown
        data = [
            {
                "id": app.id,
                "name": app.application_name,
                "count": app.request_set.count(),
            }
            for app in queryset
        ]
        return Response(data)


class ApplicationRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract data fprirom request
            application_id = request.data.get("applicationID")
            student_id = request.data.get("studentID")
            comment = request.data.get("comments", None)  # Optional comment
            if comment:
                comment_data = [
                    {
                        "name": request.user.name,
                        "text": comment,
                        "type": request.user.user_type,
                        "timestamp": datetime.now().isoformat(),
                    }
                ]
            else:
                comment_data = []
            request_file = request.FILES.get("request_file", None)  # Handle file upload
            # Validate required fields
            if not all([application_id, student_id]):
                return Response(
                    {
                        "status": "error",
                        "message": "applicationID and studentID are required",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify application exists
            try:
                application = Applications.objects.get(id=application_id)
            except ObjectDoesNotExist:
                return Response(
                    {"status": "error", "message": "Invalid application ID"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            employee_id = application.default_responsible_employee_id
            try:
                employee = Users.objects.get(user_id=employee_id)
            except ObjectDoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid employeeId",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Verify applicant exists
            try:
                applicant = Users.objects.get(uu_id=student_id)
            except Users.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid studentID: User does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch the template text from the application
            template_text = application.application_desc

            # Prepare data to replace the placeholders in the template
            pattern = re.match(r"([A-Za-z]+)([0-9]+)", applicant.uu_id)
            template_data = {
                "student_name": applicant.name,
                "registration_no": applicant.uu_id,
                "department": applicant.dept.dept_name,
                "program": applicant.program.program_name if applicant.program else "",
                "date": timezone.now().date(),
                "issuer_name": application.default_responsible_employee,
                "father_name": applicant.father_name,
                "address": applicant.address,
                "gender": applicant.gender,
                "status": applicant.status,
                "email": applicant.email,
                "created_at": applicant.created_at,
                "updated_at": applicant.updated_at,
                "user_type": applicant.user_type,
                "role": applicant.role,
                "designation": applicant.designation,
                "remark": applicant.remark,
                "phone_number": applicant.phone_number,
                "picture": applicant.picture,
                "cgpa": applicant.cgpa,
                "current_term": applicant.term,
                "enrolled_term": extract_year_term(pattern.group(2)),
                "dob": applicant.DoB,
                "cnic": applicant.CNIC,
                "He/She": "He" if applicant.gender.lower() == "male" else "She",
                "His/Her": "His" if applicant.gender.lower() == "male" else "Her",
                "parent_relationship": (
                    "S/O" if applicant.gender.lower() == "male" else "D/O"
                ),
            }

            # Replace placeholders in the template text
            rendered_template = template_text.format(**template_data)

            # Prepare serializer data
            request_data = {
                "application": application_id,
                "applicant": applicant.user_id,
                "status": "Pending",
                "payment_status": "Pending",
                "StudentID": applicant.user_id,
                "EmployeeID": employee_id,
                "renderedtemplate": rendered_template,
                "comments": comment_data,
                "created_at": datetime.now().isoformat(),  # This ensures it's timezone-aware
                "updated_at": datetime.now().isoformat(),
                "request_file": request_file,  # Include the file in request data
            }

            logger.info("Serializer data: %s", request_data)

            # Use serializer to validate and save
            serializer = RequestSerializer(data=request_data)
            if serializer.is_valid():
                logger.info("Serializer is valid")
                new_request = serializer.save()
                send_alert_email(
                    employee.email,
                    "New Application request Generated",
                    "A new application has been submitted. Please review it at your earliest convenience.",
                    recipient_name=employee.name,
                )
                logger.info("Request created: %s", new_request.request_id)
            else:
                logger.error("Serializer errors: %s", serializer.errors)
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid request data",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Prepare response data
            response_data = {
                "status": "success",
                "message": "Application request created successfully",
                "data": {
                    "request_id": new_request.request_id,
                    "application_id": new_request.application_id,
                    "student_id": new_request.StudentID,
                    "status": new_request.status,
                    "created_at": new_request.created_at.isoformat(),
                    "renderedtemplate": new_request.renderedtemplate,
                    "comments": new_request.comments,
                },
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in ApplicationRequestAPIView: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while processing your request",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AllUsersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = Users.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"


def convocation(request):
    return render(request, "CUSTApp/AdminDashboard/convocation.html")


def about(request):
    return HttpResponse("This is the about page.")


def login(request):
    return render(request, "CUSTApp/login.html")


def students(request):
    return render(request, "CUSTApp/AdminDashboard/students.html")


# D:\CustApp\project\CUSTApp\templates\CUSTApp\AdminDashboard\students.html


def dashboard(request):
    return render(request, "CUSTApp/dashboard.html")


def privacy_policy(request):
    return render(request, "CUSTApp/UserDashboard/privacy-policy.html")


def verify_otp_page(request):
    return render(request, "CUSTApp/verify_otp.html")


def index_page(request):
    return render(request, "CUSTApp/index.html")


def complaints(request):
    complaint_stats = [
        {"key": "pending", "label": "PENDING", "icon": "hourglass_empty"},
        {"key": "resolved", "label": "RESOLVED", "icon": "check_circle"},
        {"key": "rejected", "label": "REJECTED", "icon": "cancel"},
        {"key": "total", "label": "TOTAL", "icon": "list_alt"},
    ]
    return render(
        request,
        "CUSTApp/UserDashboard/complaints.html",
        {"complaint_stats": complaint_stats},
    )


def test_api_view(request):
    return render(request, "CUSTApp/test_api.html")


from rest_framework.filters import SearchFilter


# Generic API Views
class UsersList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "uu_id"]

    def get_queryset(self):
        department = self.request.query_params.get("department")
        user_type = self.request.query_params.get("user_type")
        show_all = self.request.query_params.get("all", "False").lower() == "true"

        if show_all:
            return Users.objects.all()

        queryset = Users.objects.all()

        if department:
            queryset = queryset.filter(dept=department)
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        if department or user_type:
            return queryset.order_by("name")

        try:
            return Users.objects.filter(user_id=self.request.user.user_id)
        except Users.DoesNotExist:
            return Users.objects.none()


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Users.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "user_id"

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.user_id != user.user_id:
            return Response(
                {"error": "The user can only update his profile!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User data updated sucessfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Department.objects.all().order_by("dept_name")
    serializer_class = DepartmentSerializer


class DepartmentRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    lookup_field = "dept_id"


class RequestList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_serializer_class(self):
        request_type = self.request.query_params.get("type", "Application")
        if request_type == "Application":
            return RequestSerializer
        elif request_type == "Complaint":
            return ComplaintSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        user_type = user.user_type
        if user_type == "Student":
            queryset = queryset.filter(StudentID=user.user_id)
        if user_type == "Staff":
            queryset = queryset.filter(EmployeeID=user.user_id)
        return queryset


class RequestDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Users.objects.none()  # or a safe fallback

        queryset = super().get_queryset()
        user = self.request.user
        user_type = user.user_type
        if user_type == "Student":
            queryset = queryset.filter(StudentID=user.user_id)
        if user_type == "Staff":
            queryset = queryset.filter(EmployeeID=user.user_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        user_type = str(user.user_type)
        if user_type.lower() == "student" and instance.StudentID != user.user_id:
            return Response(
                {"error": "This application Does not belong to current user!"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)


class GetAttributesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model_fields(self, model_name):
        try:
            model = apps.get_model("CUSTApp", model_name)
            return [field.name for field in model._meta.fields]
        except LookupError:
            return []

    @swagger_auto_schema(
        operation_description="Get model attributes dynamically by table name",
        manual_parameters=[
            openapi.Parameter(
                "table",
                openapi.IN_QUERY,
                description="Name of the model/table (e.g., 'Users')",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of attribute names",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        table = request.GET.get("table")
        attributes = []
        user_type = request.GET.get("user_type", "")
        if not table:
            return Response([])
        if table == "Convocation":
            attributes = self.get_model_fields("Convocation")
            print(attributes)
        elif table == "users":
            attributes = [
                "student_name",
                "email",
                "father_name",
                "registration_no",
                "address",
                "program",
                "department",
                "gender",
                "status",
                "user_type",
                "role",
                "designation",
                "remark",
                "phone_number",
                "cgpa",
                "term",
                "DoB",
                "cnic",
            ]
            if user_type == "staff":
                attributes[0] = "name"
            else:
                attributes[0] = "student_name"

        elif table == "users" and user_type == "student":
            attributes[0] = "student_name"
        elif table == "Misc":
            attributes = ["He/She", "His/Her", "parent_relationship"]
        return Response(attributes)


# OTP APIs with jwt token
class OTPSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        # platform = request.data.get("platform")

        # Check if user exists
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response(
                {"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND
            )
        # if platform == "mobile" and user.user_type.lower() != "student":
        #     return Response(
        #         {
        #             "error": "Only students can login through mobile app!",
        #             "status": status.HTTP_403_FORBIDDEN,
        #         }
        #     )
        # Generate a 6-digit OTP
        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        if email == "zohaib.ahmed1397@gmail.com":
            user.otp = "000000"
        else:
            user.otp = otp
        user.save()

        # Send OTP via email

        subject = "Your OTP for CUSTApp Login"

        message = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f5f7fa; padding: 20px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
      <tr>
        <td style="padding: 30px; text-align: center;">
          <h2 style="color: #1a73e8; margin-bottom: 10px;">CUSTApp Login Verification</h2>
          <p style="font-size: 16px; color: #333;">Dear User,</p>
          <p style="font-size: 16px; color: #333;">Your One-Time Password (OTP) for logging into <strong>CUSTApp</strong> is:</p>
          <p style="font-size: 32px; font-weight: bold; color: #1a73e8; margin: 20px 0;">{otp}</p>
          <p style="font-size: 14px; color: #555;">This OTP is valid for <strong>10 minutes</strong>. Do not share this code with anyone.</p>
          <hr style="margin: 30px 0;">
          <p style="font-size: 13px; color: #999;">If you did not request this code, please ignore this email or contact support at <a href="mailto:support@custapp.pk" style="color: #1a73e8;">support@cust.edu.pk</a>.</p>
          <p style="font-size: 13px; color: #999;">© {datetime.now().year} Capital University of Science & Technology. All rights reserved.</p>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

        from_email = (
            settings.EMAIL_HOST_USER
            if settings.EMAIL_HOST_USER
            else "support@custapp.pk"
        )
        threading.Thread(
            target=send_email_async,
            args=(subject,message,from_email,email)
        ).start()

        return Response(
            {"message": "OTP sent to your email."}, status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if "phone_number" in self.request.data:
            return PhoneOTPVerifySerializer
        return OTPVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data.get(
            "email"
        ) or serializer.validated_data.get("phone_number")
        print(identifier)
        otp = serializer.validated_data["otp"]
        try:
            if "email" in serializer.validated_data:
                user = Users.objects.get(email=identifier)
            else:
                user = Users.objects.get(phone_number=identifier)
            if user.otp == otp:
                # OTP matched, clear it after successful login

                if (
                    user.email != "zohaib.ahmed1397@gmail.com"
                ):  # Permanent otp for an email
                    user.otp = None
                user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                print(
                    f"Generated Tokens - Access: {access_token}, Refresh: {refresh_token}"
                )  # Log tokens

                if user.user_type == "admin":
                    dashboard_url = "/admin/dashboard/"
                else:
                    dashboard_url = "/user/dashboard/"

                return Response(
                    {
                        "message": "Login successful.",
                        "user_id": user.user_id,
                        "uu_id": user.uu_id,
                        "name": user.name,
                        "email": user.email,
                        "phone_no": user.phone_number,
                        "father_name": user.father_name,
                        "cnic": user.CNIC,
                        "gender": user.gender,
                        "dob": user.DoB,
                        "passport_number": user.passport_number,
                        "user_type": user.user_type,
                        "access": access_token,
                        "refresh": refresh_token,
                        "dashboard_url": dashboard_url,
                        "profile_picture": user.picture.url if user.picture else None,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout sucessfully"}, status=status.HTTP_205_RESET_CONTENT
            )
        except KeyError:
            return Response(
                {"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError:
            return Response(
                {"error": "Invalide Refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )


# Path to the predefined letterhead PDF
LETTERHEAD_PATH = os.path.join(
    os.path.dirname(__file__), "..", "static", "LetterHead", "LetterHead.pdf"
)


class GeneratePDFWithLetterheadAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Extract request_id from JSON
        request_id = request.data.get("request_id")
        if not request_id:
            return Response(
                {"error": "request_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch request data
        try:
            request_obj = Request.objects.get(request_id=request_id)
            serializer = RequestSerializer(request_obj)
        except Request.DoesNotExist:
            return Response(
                {"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check status
        if request_obj.status != "Approved":
            return Response(
                {"error": "Request is not approved"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Extract renderedtemplate
        content = request_obj.renderedtemplate or "No content available"

        # Verify letterhead exists
        if not os.path.exists(LETTERHEAD_PATH):
            return Response(
                {"error": "Letterhead PDF not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        content_buffer = BytesIO()
        doc = SimpleDocTemplate(
            content_buffer,
            pagesize=letter,
            leftMargin=0,
            rightMargin=0,
            topMargin=0,
            bottomMargin=0,
        )
        elements = []

        # Define styles for text
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Image
        from reportlab.platypus import Table, TableStyle

        # Define custom styles
        styles = getSampleStyleSheet()

        # Main body text style (left-aligned, no forced indent)
        body_style = ParagraphStyle(
            name="BodyText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            alignment=4,  # Left align
            leftIndent=52,  # No left indent
            rightIndent=72,  # No right indent
            spaceBefore=0,
            spaceAfter=12,
        )

        # Date style (right-aligned)
        date_style = ParagraphStyle(
            name="DateText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=14,
            alignment=2,  # Right align
            rightIndent=72,  # ~1 inch from right
            leftIndent=0,
        )

        # Signature style (left-aligned, with indent matching letter format)
        signature_style = ParagraphStyle(
            name="SignatureText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=14,
            alignment=0,  # Left align
            leftIndent=0,  # ~1.5 inch indent
            rightIndent=0,
        )

        # Build your elements
        elements = []
        # Signature image
        signature_image_path = os.path.join(
            settings.MEDIA_ROOT, serializer.data.get("responsible_employee_signature")
        )
        print(signature_image_path)
        signature_image = Image(signature_image_path, width=128, height=64)

        # 1. Add date (right-aligned)
        current_date = timezone.now().strftime("%B %d, %Y")  # e.g., "November 12, 2024"
        elements.append(Spacer(1, 70))  # Space from top
        elements.append(Paragraph(current_date, date_style))
        elements.append(Spacer(1, 70))  # Space after date

        # 2. Add main content (left-aligned, no indent)
        for line in content.split("\n"):
            elements.append(Paragraph(line, body_style))

        # --- QR Code Footer Section ---

        # Generate verification URL (adjust 'request-verification' to your actual URL name)
        verify_url = request.build_absolute_uri(
            reverse("request-verification", args=[request_obj.request_id])
        )

        # Generate QR code
        qr = qrcode.QRCode(box_size=3, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_image = RLImage(qr_buffer, width=60, height=60)
        # QR code text and URL paragraph
        from reportlab.lib import colors

        verify_note_style = ParagraphStyle(
            name="VerifyNote",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            alignment=0,  # Left align
            textColor=colors.grey,
        )

        qr_note = Paragraph(
            "Scan the QR code to verify this document.", verify_note_style
        )
        qr_link = Paragraph(
            f"<a href='{verify_url}' color='blue'>{verify_url}</a>", verify_note_style
        )

        # Signature section (image + name + designation + department)
        signature_data = [
            signature_image,
            Paragraph(
                serializer.data.get("responsible_employee_name"), signature_style
            ),
            Paragraph(
                serializer.data.get("responsible_employee_designation"), signature_style
            ),
            Paragraph(serializer.data.get("responsible_dept_name"), signature_style),
        ]

        signature_table = Table([[s] for s in signature_data], colWidths=[150])
        signature_table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        # QR section (QR image + small note + link)
        qr_table = Table([[qr_image], [qr_note], [qr_link]], colWidths=[200])
        qr_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        # Combine signature and QR into one horizontal row
        final_footer_table = Table(
            [[signature_table, qr_table]],
            colWidths=[300, 200],  # Adjust width as needed
        )
        final_footer_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        elements.append(Spacer(1, 30))
        elements.append(final_footer_table)
        # Build the PDF
        doc.build(elements)
        content_buffer.seek(0)

        # p.drawText(text_object)

        # p.showPage()
        # p.save()
        # content_buffer.seek(0)

        # Merge letterhead and content
        letterhead_pdf = PdfReader(LETTERHEAD_PATH)
        content_pdf = PdfReader(content_buffer)
        output = PdfWriter()

        for page_num in range(len(letterhead_pdf.pages)):
            page = letterhead_pdf.pages[page_num]
            if page_num < len(content_pdf.pages):
                content_page = content_pdf.pages[page_num]
                page.merge_page(content_page)
            output.add_page(page)

        # Create output buffer
        output_buffer = BytesIO()
        output.write(output_buffer)
        output_buffer.seek(0)
        pdf = output_buffer.getvalue()

        # Clean up
        content_buffer.close()
        output_buffer.close()

        # Return PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{request_obj.applicant.uu_id} - {request_obj.application.application_name}"'
        )
        response.write(pdf)
        return response


class ProgramView(ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        program_name = self.request.query_params.get("program_name")
        if program_name:
            queryset = queryset.filter(program_name=program_name)
        return queryset


def admin_dashboard(request):
    return render(request, "CUSTApp/AdminDashboard/index.html")


def admin_faculty(request):
    return render(request, "CUSTApp/AdminDashboard/faculty.html")


def admin_department(request):
    return render(request, "CUSTApp/AdminDashboard/departments.html")


def admin_templates(request):
    return render(request, "CUSTApp/AdminDashboard/templates.html")


def user_dashboard(request):
    context = {"page_title": "Dashboard", "active_page": "dashboard"}
    return render(request, "CUSTApp/UserDashboard/index.html", context)


def view_applications(request):
    return render(request, "CUSTApp/UserDashboard/applications.html")


def categories(request):
    return render(request, "CUSTApp/UserDashboard/categories.html")


def new_application(request):
    return render(request, "CUSTApp/UserDashboard/new-application.html")


def reports(request):
    return render(request, "CUSTApp/UserDashboard/reports.html")


def user_profile(request):
    return render(request, "CUSTApp/UserDashboard/profile.html")


def support(request):
    return render(request, "CUSTApp/UserDashboard/support.html")


def guest_pass(request):
    return render(request, "CUSTApp/UserDashboard/guest_pass.html")


def public_guest_pass(request, pass_id=None):
    if not pass_id:
        return render(request, "CUSTApp/UserDashboard/guest_pass_open.html")
    guest_pass = get_object_or_404(Request, request_id=pass_id)
    if guest_pass.meeting_date_time:
        guest_pass.meeting_date = guest_pass.meeting_date_time.date()
        guest_pass.meeting_time = guest_pass.meeting_date_time.time().strftime(
            "%I:%M %p"
        )
    context = {"public_pass_view": True, "guest_pass": guest_pass}
    return render(
        request, "CUSTApp/UserDashboard/guest_pass_open.html", context=context
    )


def home(request):
    return render(request, "CUSTApp/Home.html")


class SupportTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        issue_description = request.data.get("issue_description", "")
        user = request.user

        if not issue_description:
            return Response({"message": "Issue description is required."}, status=400)

        # Compose the email
        subject = "New Support Ticket"
        message = (
            f"From: {user.email}\nUser: {user.name}\n\nIssue:\n{issue_description}"
        )
        from_email = "no-reply@custapp.pk"
        recipient_list = ["support@custapp.pk"]

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return Response({"message": "Support ticket submitted successfully."})
        except Exception as e:
            return Response({"message": f"Failed to send email: {str(e)}"}, status=500)


class RequestRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    lookup_field = "request_id"


def request_verification_page(request, request_id):
    req = get_object_or_404(Request, request_id=request_id)
    return render(request, "CUSTApp/request_verification.html", {"req": req})
