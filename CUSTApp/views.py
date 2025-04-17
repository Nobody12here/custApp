# CUSTApp/views.py
from datetime import datetime
from io import BytesIO
from django.core.mail import EmailMultiAlternatives
import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from ApplicationTemplate.models import Applications, Request
from .models import Program, Users, Department, TemplateAttributes
from ApplicationTemplate.serializers import ApplicationsSerializer, RequestSerializer
from .serializers import (
    ProgramSerializer,
    UsersSerializer,
    DepartmentSerializer,
    TemplateAttributesSerializer,
    OTPSendSerializer,
    OTPVerifySerializer,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser

import csv
import io
from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
from rest_framework.viewsets import ModelViewSet
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ApplicationTemplate.models import Applications
from .models import Users
from .serializers import RequestSerializer
import json
logger = logging.getLogger(__name__)

from django.utils import timezone
def add_comment(request, id):
    if request.method == 'POST':
        text = request.POST.get('text')
        if not text:
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        try:
            req = Request.objects.get(pk=id)
            # Determine user info
            name = request.user.get_full_name() or request.user.username
            user_type = 'employee' if request.user.groups.filter(name='Employees').exists() else 'student'
            # Initialize comments
            comments = json.loads(req.comments) if req.comments else []
            # Add new comment
            new_comment = {
                'name': name,
                'text': text,
                'type': user_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            comments.append(new_comment)
            req.comments = json.dumps(comments)
            req.save()
            return JsonResponse({'success': True})
        except Request.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid comment format'}, status=400)
        except AttributeError:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def update_request_status(request, id):
    if request.method == 'POST':
        status = request.POST.get('status')
        if status not in ['Approved', 'Rejected']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        try:
            req = Request.objects.get(pk=id)
            req.status = status
            req.save()
            return JsonResponse({'success': True})
        except Request.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)
def update_rendered_template(request, id):
    if request.method == 'POST':
        content = request.POST.get('content')
        try:
            req = Request.objects.get(pk=id)
            req.renderedtemplate = content
            req.save()
            return JsonResponse({'success': True})
        except Request.DoesNotExist:
            return JsonResponse({'error': 'Request not found'}, status=404)
class ApplicationListView(generics.ListAPIView):
    permission_classes = [AllowAny]

    queryset = Applications.objects.filter(status=1)  # Only enabled applications
    serializer_class = ApplicationsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Return only id and application_name for the dropdown
        data = [{"id": app.id, "name": app.application_name} for app in queryset]
        return Response(data)


class ApplicationRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Extract data from request
            application_id = request.data.get("applicationID")
            student_id = request.data.get("studentID")
            comment = request.data.get("comments", None)  # Optional comment
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
            app_name = application.application_name
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

            # Fetch the template text from the application
            template_text = application.application_desc

            # Prepare data to replace the placeholders in the template
            template_data = {
                "student_name": applicant.name,
                "registration_no": applicant.uu_id,
                "department": applicant.dept_name,
                "program": applicant.program_name,
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
                "term": applicant.term,
                "dob": applicant.DoB,
                "cnic": applicant.CNIC,
            }

            # Replace placeholders in the template text
            rendered_template = template_text.format(**template_data)

            # Prepare serializer data
            request_data = {
                "application": application_id,
                "applicant": student_id,
                "status": "Pending",
                "payment_status": "Pending",
                "StudentID": student_id,
                "EmployeeID": employee_id,
                "renderedtemplate": rendered_template,
                "comments": comment if comment else "",
                "request_file": request_file,  # Include the file in request data
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


class UserCSVUploadAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")
        user_type = request.data.get("user_type")
        if not csv_file or not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Please upload a valid CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created_users = []
            for row in reader:
                serializer = UsersSerializer(data=row)
                if serializer.is_valid():
                    if user_type == "student":
                        serializer.validated_data["user_type"] = "Student"
                        serializer.validated_data["role"] = "Undergraduate"
                        serializer.validated_data["designation"] = "N/A"
                    elif user_type == "staff":
                        serializer.validated_data["user_type"] = "Staff"
                    serializer.save()
                    created_users.append(serializer.data)
                else:
                    return Response(
                        {
                            "error": f"Invalid data in row: {row}",
                            "details": serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {"message": "Users uploaded successfully.", "data": created_users},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepartmentList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
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


class ApplicationsList(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated]  # ROLE based permission_classes = [IsAuthenticated, IsAdminUser]
    permission_classes = [AllowAny]
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer


# Template API via Applications


class TemplateListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer

    def get_queryset(self):
        return Applications.objects.filter(status=1)


class TemplateRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer
    lookup_field = "id"


class TemplateDisableAPIView(generics.DestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 0
        instance.save()
        return Response(
            {"message": "Application disabled successfully"}, status=status.HTTP_200_OK
        )


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
        pdfkit.from_string(rendered_content, False)
        pdf_file.seek(0)

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{template_name}.pdf"'
        return response


class GetAttributesAPIView(APIView):
    permission_classes = [AllowAny]

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
        if table == "users":
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
        elif table == "Department":
            attributes = ["dept_id", "dept_name", "dept_head", "short_name"]
        elif table == "Applications":
            attributes = [
                "id",
                "application_name",
                "short_name",
                "application_desc",
                "status",
                "responsible_dept",
                "amount",
                "default_responsible_employee",
            ]
        elif table == "Program":
            attributes = [
                "program_id",
                "program_name",
                "short_name",
                "program_desc",
                "status",
                "dept_name",
            ]

        return Response(attributes)


# OTP APIs with jwt token
class OTPSendView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSendSerializer

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
          <p style="font-size: 13px; color: #999;">If you did not request this code, please ignore this email or contact support at <a href="mailto:support@cust.edu.pk" style="color: #1a73e8;">support@cust.edu.pk</a>.</p>
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
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[email]
        )
        email_message.attach_alternative(message,'text/html')
        email_message.send()

        return Response(
            {"message": "OTP sent to your email."}, status=status.HTTP_200_OK
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer

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
    return render(request, "CUSTApp/UserDashboard/index.html")


def view_applications(request):

    return render(request, "CUSTApp/UserDashboard/applications.html")


def categories(request):

    return render(request, "CUSTApp/UserDashboard/categories.html")


def new_application(request):

    return render(request, "CUSTApp/UserDashboard/new-application.html")


def reports(request):

    return render(request, "CUSTApp/UserDashboard/reports.html")
