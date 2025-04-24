# CUSTApp/views.py
from datetime import datetime
from io import BytesIO
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.apps import apps
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from ApplicationTemplate.models import Applications, Request
from .models import Program, Users, Department
from ApplicationTemplate.serializers import ApplicationsSerializer, RequestSerializer
from .serializers import (
    ProgramSerializer,
    UsersSerializer,
    DepartmentSerializer,
    OTPSendSerializer,
    OTPVerifySerializer,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser
from .utils import send_alert_email
import csv
import io
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
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
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


class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            text = request.data.get("text")
            if not text:
                return Response(
                    {"error": "Comment text is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            req = Request.objects.get(pk=id)
            # User info
            name = request.user.name
            user_type = request.user.user_type

            # Load and update comments
            try:
                comments = json.loads(req.comments) if req.comments else []
            except Exception:
                comments = []
            new_comment = {
                "name": name,
                "text": text,
                "type": user_type,
                "timestamp": timezone.now().isoformat(),
            }
            comments.append(new_comment)
            req.comments = json.dumps(comments)
            req.save()

            return Response({"success": True})

        except Request.DoesNotExist:
            return Response(
                {"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid comment format"}, status=status.HTTP_400_BAD_REQUEST
            )


def update_request_status(request, id):
    if request.method == "POST":
        status = request.POST.get("status")
        if status not in ["Approved", "Rejected"]:
            return JsonResponse({"error": "Invalid status"}, status=400)
        try:
            req = Request.objects.get(pk=id)
            req.status = status
            req.save()
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
        data = [{"id": app.id, "name": app.application_name} for app in queryset]
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
                return Response({
                    "status":"error","message":"Invalid employeeId",}
                    ,status=status.HTTP_404_NOT_FOUND)
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
                "comments": comment_data,
                "request_file": request_file,  # Include the file in request data
            }

            logger.info("Serializer data: %s", request_data)

            # Use serializer to validate and save
            serializer = RequestSerializer(data=request_data)
            if serializer.is_valid():
                logger.info("Serializer is valid")
                new_request = serializer.save()
                send_alert_email(employee.email,"New Application request Generated","A new application has been submitted. Please review it at your earliest convenience.",recipient_name=employee.name)
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
                        serializer.validated_data["user_type"] = "Faculty"
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
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        user_type = user.user_type
        if user_type == "Student":
            queryset = queryset.filter(StudentID=user.user_id)
        if user_type == "Staff":
            queryset = queryset.filter(EmployeeID=user.user_id)
        return queryset


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
            attributes = ["department"]
        elif table == "Application":
            attributes = ["date", "issuer_name"]
        elif table == "Program":
            attributes = ["program"]

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
        email_message = EmailMultiAlternatives(
            subject=subject, body=message, from_email=from_email, to=[email]
        )
        email_message.attach_alternative(message, "text/html")
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


import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

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

        # Define custom styles
        styles = getSampleStyleSheet()

        # Main body text style (left-aligned, no forced indent)
        body_style = ParagraphStyle(
            name="BodyText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=14,
            alignment=0,  # Left align
            leftIndent=90,  # No left indent
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
            leftIndent=90,  # ~1.5 inch indent
            rightIndent=0,
        )

        # Build your elements
        elements = []

        # 1. Add date (right-aligned)
        current_date = timezone.now().strftime("%B %d, %Y")  # e.g., "November 12, 2024"
        elements.append(Spacer(1, 70))  # Space from top
        elements.append(Paragraph(current_date, date_style))
        elements.append(Spacer(1, 70))  # Space after date

        # 2. Add main content (left-aligned, no indent)
        for line in content.split("\n"):
            elements.append(Paragraph(line, body_style))

        # 3. Add signature (indented left)
        elements.append(Spacer(1, 70))
        elements.append(Paragraph("Issued on request", signature_style))
        elements.append(Spacer(1, 70))
        elements.append(
            Paragraph(serializer.data.get("responsible_employee_name"), signature_style)
        )

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
        response["Content-Disposition"] = 'attachment; filename="letter.pdf"'
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
    return render(
        request,
        "CUSTApp/UserDashboard/index.html",
    )


def view_applications(request):

    return render(request, "CUSTApp/UserDashboard/applications.html")


def categories(request):

    return render(request, "CUSTApp/UserDashboard/categories.html")


def new_application(request):

    return render(request, "CUSTApp/UserDashboard/new-application.html")


def reports(request):

    return render(request, "CUSTApp/UserDashboard/reports.html")

def support(request):

    return render(request, "CUSTApp/UserDashboard/support.html")
