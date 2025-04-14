# CUSTApp/views.py
from io import BytesIO
import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from ApplicationTemplate.models import Request,Applications
from .models import Users, Department, TemplateAttributes
from ApplicationTemplate.serializers import RequestSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UsersSerializer,
    DepartmentSerializer,
    TemplateAttributesSerializer,
    OTPSendSerializer,
    OTPVerifySerializer,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.utils import timezone
import logging
import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.decorators import login_required
import pdfkit


logger = logging.getLogger(__name__)

import logging
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import  Users
from ApplicationTemplate.serializers import RequestSerializer

logger = logging.getLogger(__name__)


class ApplicationRequestAPIView(APIView):
    # Uncomment if you enable authentication later
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Extract data from request
            application_id = request.data.get("applicationID")
            student_id = request.data.get("studentID")

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

            # Verify applicant exists
            try:
                applicant = Users.objects.get(user_id=student_id)
            except Users.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid studentID: User does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Prepare serializer data
            request_data = {
                "application": application_id,
                "applicant": student_id,  # Use student_id as user_id
                "status": "Pending",
                "payment_status": "Pending",
                "studentID": student_id,
            }
            logger.info("Serializer data: %s", request_data)

            # Use serializer to validate and save
            serializer = RequestSerializer(data=request_data)
            if serializer.is_valid():
                logger.info("Serializer is valid")
                new_request = serializer.save()
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
                    "student_id": new_request.studentID,
                    "status": new_request.status,
                    "created_at": new_request.created_at.isoformat(),
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


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"


# Basic Views
def home(request):
    # return HttpResponse(request, 'CUSTApp/login.html')
    return HttpResponse("CUSTApp Django!")


def about(request):
    return HttpResponse("This is the about page.")


def login(request):
    return render(request, "CUSTApp/login.html")


def students(request):
    return render(request, "CUSTApp/AdminDashboard/students.html")


# D:\CustApp\project\CUSTApp\templates\CUSTApp\AdminDashboard\students.html


def dashboard(request):
    return render(request, "CUSTApp/dashboard.html")


def verify_otp_page(request):
    return render(request, "CUSTApp/verify_otp.html")


def index_page(request):
    return render(request, "CUSTApp/index.html")


def test_api_view(request):
    return render(request, "CUSTApp/test_api.html")


# Generic API Views
class UsersList(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Users.objects.all()
    serializer_class = UsersSerializer


class UserRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]  # Only admins can modify users
    lookup_field = "user_id"


class DepartmentList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    lookup_field = "dept_id"


class RequestList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        applicant_id = self.request.query_params.get("applicant_id")
        dept_id = self.request.query_params.get("dept_id")
        if applicant_id:
            queryset = queryset.filter(applicant_id=applicant_id)
        if dept_id:
            queryset = queryset.filter(application__responsible_dept_id=dept_id)
        return queryset


class TemplateAttributesList(generics.ListCreateAPIView):
    queryset = TemplateAttributes.objects.all()
    serializer_class = TemplateAttributesSerializer


# class ApplicationsList(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     # permission_classes = [IsAuthenticated]  # ROLE based permission_classes = [IsAuthenticated, IsAdminUser]
#     # permission_classes = [AllowAny]
#     queryset = Applications.objects.all()
#     serializer_class = ApplicationsSerializer


# Template API via Applications


# class TemplateListCreateAPIView(generics.ListCreateAPIView):
#     permission_classes = [AllowAny]
#     queryset = Applications.objects.all()
#     serializer_class = ApplicationsSerializer

#     def get_queryset(self):
#         return Applications.objects.filter(status=1)


# class TemplateRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     permission_classes = [AllowAny]
#     queryset = Applications.objects.all()
#     serializer_class = ApplicationsSerializer
#     lookup_field = "id"


# class TemplateDisableAPIView(generics.DestroyAPIView):
#     permission_classes = [AllowAny]
#     queryset = Applications.objects.all()
#     serializer_class = ApplicationsSerializer
#     lookup_field = "id"

#     def delete(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.status = 0
#         instance.save()
#         return Response(
#             {"message": "Application disabled successfully"}, status=status.HTTP_200_OK
#         )


class RequestCreate(APIView):
    permission_classes = [AllowAny]

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        logger.info(f"Received data: {request.data}")
        request_serializer = RequestSerializer(
            data={
                "application": request.data.get("application_id"),
                "applicant": request.data.get("applicant_id"),
                "status": "Pending",
                "comments": request.data.get("comments", ""),
            }
        )
        if request_serializer.is_valid():
            request_instance = request_serializer.save()
            attributes_data = request.data.get("attributes", {})
            for key, value in attributes_data.items():
                TemplateAttributes.objects.create(
                    attribute_name=f"request_{request_instance.request_id}_{key}",
                    attribute_value=str(value),
                )
            return Response(request_serializer.data, status=status.HTTP_201_CREATED)
        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateLetterAPIView(APIView):
    def get(self, request, request_id):
        try:
            request_obj = Request.objects.get(request_id=request_id)
            application = request_obj.application
            student = request_obj.applicant
            issuer = application.default_responsible_employee

            if application.status != 1:
                return Response(
                    {"error": "Application is disabled"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            template = application.application_desc
            if not template:
                return Response(
                    {"error": "Template not found for this application"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            attributes = {
                attr.attribute_name.split("_", 2)[-1]: attr.attribute_value
                for attr in TemplateAttributes.objects.filter(
                    attribute_name__startswith=f"request_{request_id}_"
                )
            }
            attributes.update(
                {
                    "student_name": student.name,
                    "father_name": student.father_name or "",
                    "registration_no": student.uu_id,
                    "program": student.program_name or "",
                    "department": student.dept_name or "",
                    "date": timezone.now().strftime("%B %d, %Y"),
                    "issuer_name": issuer.name,
                    "amount": str(application.amount),
                }
            )

            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(
                Paragraph(
                    "Capital University of Science and Technology", styles["Heading1"]
                )
            )
            elements.append(Paragraph("Islamabad", styles["Normal"]))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Date: {attributes['date']}", styles["Normal"]))
            elements.append(Spacer(1, 12))

            formatted_content = template.format(**attributes)
            elements.append(Paragraph(formatted_content, styles["Normal"]))

            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Issued on request", styles["Normal"]))
            elements.append(Spacer(1, 12))
            elements.append(
                Paragraph(
                    f"{attributes['issuer_name']}\nDeputy Registrar", styles["Normal"]
                )
            )

            doc.build(elements)
            pdf_buffer.seek(0)

            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=f'{application.short_name.replace("_", " ")}_{student.uu_id}.pdf',
            )
        except Request.DoesNotExist:
            return Response(
                {"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeneratePDFAPIView(APIView):
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        template_name = request.data.get("name")
        template_content = request.data.get("content")

        # Fetch user data (assuming the user is logged in)
        user = request.user  # This assumes you're using Django's authentication system
        user_data = {
            "users": {
                "student": {
                    "name": user.name if user.user_type == "student" else "",
                    "email": user.email if user.user_type == "student" else "",
                    "father_name": (
                        user.father_name if user.user_type == "student" else ""
                    ),
                    "address": user.address if user.user_type == "student" else "",
                    "program_name": (
                        user.program_name if user.user_type == "student" else ""
                    ),
                    "dept_name": user.dept_name if user.user_type == "student" else "",
                    "gender": user.gender if user.user_type == "student" else "",
                    "status": user.status if user.user_type == "student" else "",
                    "role": user.role if user.user_type == "student" else "",
                    "designation": (
                        user.designation if user.user_type == "student" else ""
                    ),
                    "remark": user.remark if user.user_type == "student" else "",
                    "phone_number": (
                        user.phone_number if user.user_type == "student" else ""
                    ),
                    "cgpa": str(user.cgpa) if user.cgpa else "",
                    "term": user.term if user.user_type == "student" else "",
                    "DoB": str(user.DoB) if user.DoB else "",
                    "CNIC": user.CNIC if user.user_type == "student" else "",
                },
                "staff": {
                    "name": user.name if user.user_type == "staff" else "",
                    "email": user.email if user.user_type == "staff" else "",
                    "father_name": (
                        user.father_name if user.user_type == "staff" else ""
                    ),
                    "address": user.address if user.user_type == "staff" else "",
                    "program_name": (
                        user.program_name if user.user_type == "staff" else ""
                    ),
                    "dept_name": user.dept_name if user.user_type == "staff" else "",
                    "gender": user.gender if user.user_type == "staff" else "",
                    "status": user.status if user.user_type == "staff" else "",
                    "role": user.role if user.user_type == "staff" else "",
                    "designation": (
                        user.designation if user.user_type == "staff" else ""
                    ),
                    "remark": user.remark if user.user_type == "staff" else "",
                    "phone_number": (
                        user.phone_number if user.user_type == "staff" else ""
                    ),
                    "cgpa": str(user.cgpa) if user.cgpa else "",
                    "term": user.term if user.user_type == "staff" else "",
                    "DoB": str(user.DoB) if user.DoB else "",
                    "CNIC": user.CNIC if user.user_type == "staff" else "",
                },
            }
        }

        # Replace the new placeholder format [users.student.name] with actual values
        def replace_placeholders(match):
            placeholder = match.group(1)  # e.g., "users.student.name"
            keys = placeholder.split(".")
            data = user_data
            try:
                for key in keys:
                    data = data[key]
                return str(data) if data else ""
            except (KeyError, TypeError):
                return ""

        # Use regex to find and replace placeholders
        rendered_content = re.sub(
            r"\[([^\]]+)\]", replace_placeholders, template_content
        )

        # Generate PDF
        pdf_file = BytesIO()
        pdfkit.from_string(rendered_content, pdf_file)
        pdf_file.seek(0)

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{template_name}.pdf"'
        return response


class GetAttributesAPIView(APIView):
    permission_classes= [AllowAny]
    def get(self, request, *args, **kwargs):
        table = request.GET.get("table")
        user_type = request.GET.get("user_type", "")

        if table == "users":
            # Define attributes for the Users model
            attributes = [
                "name",
                "email",
                "father_name",
                "address",
                "program_name",
                "dept_name",
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
                "CNIC",
            ]
            return Response(attributes)
        # Add more tables if needed (e.g., Department, Applications)
        return Response([])


# OTP APIs with jwt token
class OTPSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSendSerializer
    @swagger_auto_schema(
        request_body=OTPSendSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                examples={"application/json": {"message": "OTP sent to your email."}},
            ),
            404: openapi.Response(
                description="Email not found",
                examples={"application/json": {"error": "Email not found."}},
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # Check if user exists
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response(
                {"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Generate a 6-digit OTP
        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        user.otp = otp
        user.save()

        # Send OTP via email
        subject = "Your OTP for CUSTApp Login"
        message = f"Your OTP is: {otp}. It is valid for 10 minutes."
        from_email = (
            settings.EMAIL_HOST_USER
            if settings.EMAIL_HOST_USER
            else "support@custapp.pk"
        )
        send_mail(subject, message, from_email, [email], fail_silently=False)

        return Response(
            {"message": "OTP sent to your email."}, status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer
    @swagger_auto_schema(request_body=OTPVerifySerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = Users.objects.get(email=email)
            if user.otp == otp:
                # OTP matched, clear it after successful login
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
                        "user_type": user.user_type,
                        "access": access_token,
                        "refresh": refresh_token,
                        "dashboard_url": dashboard_url,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )
        except Users.DoesNotExist:
            return Response(
                {"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND
            )


# @login_required
def admin_dashboard(request):
    return render(request, "CUSTApp/AdminDashboard/index.html")


# @login_required
def user_dashboard(request):
    return render(request, "CUSTApp/UserDashboard/index.html")


def view_applications(request):

    return render(request, "CUSTApp/UserDashboard/applications.html")


def categories(request):

    return render(request, "CUSTApp/UserDashboard/categories.html")


def new_application(request):

    return render(request, "CUSTApp/UserDashboard/new-application.html")


def reports(request):

    return render(request, "CUSTApp/UserDashboard/reports.html")
