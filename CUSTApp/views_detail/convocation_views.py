from io import BytesIO
from bs4 import BeautifulSoup
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from CUSTApp.models import Users, Convocation
from ApplicationTemplate.models import Applications
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.utils import timezone
from reportlab.platypus import Image, Table, TableStyle
from PyPDF2 import PdfReader, PdfWriter
from reportlab.platypus import Image as RLImage
from bs4 import BeautifulSoup
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT

import os

# Path to the predefined letterhead PDF
LETTERHEAD_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "static", "LetterHead", "LetterHead.pdf"
)


class GenerateConvocationLetterAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract parameters
        application_id = request.data.get("application_id")
        convocation_id = request.data.get("convocation_id")
        student_id = request.data.get("student_id")  # Can be uu_id or user_id
        if not application_id:
            return Response(
                {"error": "application_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not convocation_id:
            return Response(
                {"error": "convocation_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not student_id:
            return Response(
                {"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch convocation details
            convocation = Convocation.objects.get(id=convocation_id)
        except Convocation.DoesNotExist:
            return Response(
                {"error": "Convocation not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            # Fetch the application
            application = Applications.objects.get(id=application_id)
        except Applications.DoesNotExist:
            return Response(
                {"error": "Application with this ID doesnt exists"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            student = Users.objects.get(uu_id=student_id)

        except Users.DoesNotExist:
            return Response(
                {"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:

            # Generate convocation letter content
            content = self.generate_convocation_content(
                convocation, student, application
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Verify letterhead exists
        if not os.path.exists(LETTERHEAD_PATH):
            return Response(
                {"error": "Letterhead PDF not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate PDF
        responsible_employee = application.default_responsible_employee
        pdf_data = self.create_convocation_pdf(content, responsible_employee)

        # Return PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="Convocation_Letter_{student.uu_id}_{convocation.academic_year}.pdf"'
        )
        response.write(pdf_data)
        return response

    def generate_convocation_content(
        self, convocation: Convocation, student: Users, application: Applications
    ):
        """Generate the convocation letter content"""

        # Format dates
        registration_deadline = convocation.registration_deadline.strftime("%B %d, %Y")
        rehearsal_date = convocation.rehearsal_date.strftime("%B %d, %Y")
        rehearsal_time = convocation.rehearsal_time.strftime("%I:%M %p")

        # Generate content based on student details
        template_content = application.application_desc
        template_data = {
            "registration_deadline": registration_deadline,
            "rehearsal_date": rehearsal_date,
            "convocation_date": (
                convocation.convocation_date.strftime("%B %d, %Y")
                if convocation.convocation_date
                else "TBD"
            ),
            "rehearsal_time": rehearsal_time,
            "academic_year": convocation.academic_year,
        }
        try:
            content = template_content.format_map(template_data)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {str(e)}")
        return content

    def parse_html_to_reportlab_elements(self, html_content: str) -> list:
        """Converts HTML content into ReportLab flowables (Paragraphs, Spacers)."""
        styles = getSampleStyleSheet()

        # Define reusable styles
        body_style = ParagraphStyle(
            name="BodyText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            leftIndent=52,
            rightIndent=52,
            spaceBefore=0,
            spaceAfter=8,
        )

        title_style = ParagraphStyle(
            name="TitleText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            leftIndent=52,
            rightIndent=52,
            spaceBefore=20,
            spaceAfter=20,
        )

        elements = []

        soup = BeautifulSoup(html_content, "html.parser")

        for tag in soup.find_all(["p", "br"]):
            if tag.name == "br":
                elements.append(Spacer(1, 12))
                continue

            inner_html = tag.decode_contents().strip()

            if not inner_html or inner_html == "&nbsp;":
                elements.append(Spacer(1, 12))
                continue

            if "INVITATION TO CONVOCATION CEREMONY" in inner_html:
                elements.append(Paragraph(inner_html, title_style))
            else:
                elements.append(Paragraph(inner_html, body_style))

        return elements

    def create_convocation_pdf(self, content: str, responsible_employee: Users):
        """Create PDF with letterhead and convocation content"""

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

        # Define custom styles
        styles = getSampleStyleSheet()

        # Main body text style
        body_style = ParagraphStyle(
            name="BodyText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=4,  # Justify
            leftIndent=52,
            rightIndent=52,
            spaceBefore=0,
            spaceAfter=8,
        )
        # Signature style (left-aligned, with indent matching letter format)
        signature_style = ParagraphStyle(
            name="SignatureText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=14,
            alignment=0,  # Left align
            leftIndent=0,  # Match the document's left indent
            rightIndent=0,
        )
        # Title style
        title_style = ParagraphStyle(
            name="TitleText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=1,  # Center
            leftIndent=52,
            rightIndent=52,
            spaceBefore=20,
            spaceAfter=20,
        )

        # Date style (right-aligned)
        date_style = ParagraphStyle(
            name="DateText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=2,  # Right align
            rightIndent=72,
            leftIndent=0,
        )
        # Add letterhead image
        # Signature image
        signature_image = Image(responsible_employee.signature, width=128, height=64)
        # Add current date
        current_date = timezone.now().strftime("%B %d, %Y")
        elements.append(Spacer(1, 70))
        elements.append(Paragraph(current_date, date_style))
        elements.append(Spacer(1, 40))

        elements += self.parse_html_to_reportlab_elements(content)
        # signature
        signature_image.hAlign = 'LEFT'
        
        # Use the original image object with proper alignment
        signature_data = [
            signature_image,
            Paragraph(responsible_employee.name, signature_style),
            Paragraph(responsible_employee.designation, signature_style),
            Paragraph(responsible_employee.dept.dept_name + " department", signature_style),
        ]
        signature_table = Table([[s] for s in signature_data], colWidths=[350])
        signature_table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1),52),  # Match document left indent
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        signature_table.hAlign = 'LEFT'  # Align the entire table to the left
        elements.append(Spacer(1, 30))
        elements.append(signature_table)
        # Build the PDF
        doc.build(elements)
        content_buffer.seek(0)

        # Merge with letterhead
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
        pdf_data = output_buffer.getvalue()

        # Clean up
        content_buffer.close()
        output_buffer.close()

        return pdf_data


class BulkGenerateConvocationLettersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Generate convocation letters for all students in a convocation"""

        convocation_id = request.data.get("convocation_id")

        if not convocation_id:
            return Response(
                {"error": "convocation_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            convocation = Convocation.objects.get(id=convocation_id)
        except Convocation.DoesNotExist:
            return Response(
                {"error": "Convocation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get all students assigned to this convocation
        students = Users.objects.filter(convocation=convocation, user_type="Student")

        if not students:
            return Response(
                {"error": "No students found for this convocation"},
                status=status.HTTP_404_NOT_FOUND,
            )

        generated_letters = []
        errors = []

        # Generate letters for each student
        for student in students:
            try:

                # Create individual letter
                letter_generator = GenerateConvocationLetterAPIView()
                content = letter_generator.generate_convocation_content(
                    convocation, student
                )
                pdf_data = letter_generator.create_convocation_pdf(content)

                generated_letters.append(
                    {
                        "student_id": student.uu_id,
                        "student_name": student.name,
                        "status": "success",
                    }
                )

            except Exception as e:
                errors.append({"student_id": student.uu_id, "error": str(e)})

        return Response(
            {
                "message": f"Generated {len(generated_letters)} convocation letters successfully",
                "generated_count": len(generated_letters),
                "error_count": len(errors),
                "generated_letters": generated_letters,
                "errors": errors[:10] if errors else [],  # Limit errors shown
            },
            status=status.HTTP_200_OK,
        )


class SendConvocationEmailsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Send convocation invitation emails to students"""

        convocation_id = request.data.get("convocation_id")

        if not convocation_id:
            return Response(
                {"error": "convocation_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            convocation = Convocation.objects.get(id=convocation_id)
        except Convocation.DoesNotExist:
            return Response(
                {"error": "Convocation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get students for this convocation
        students = Users.objects.filter(convocation=convocation, user_type="Student")

        if not students:
            return Response(
                {"error": "No students found for this convocation"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sent_emails = []
        errors = []

        for student in students:
            try:
                # Generate email content
                subject = (
                    f"Invitation to {convocation.title} - {convocation.academic_year}"
                )

                message = f"""
Dear {student.name},

Congratulations! You are cordially invited to participate in the {convocation.title} for the {convocation.academic_year} academic year.

IMPORTANT DETAILS:
- Registration Deadline: {convocation.registration_deadline.strftime('%B %d, %Y')}
- Rehearsal Date: {convocation.rehearsal_date.strftime('%B %d, %Y')} at {convocation.rehearsal_time.strftime('%I:%M %p')}
- Registration Link: {convocation.registration_form_link}

Please register before the deadline and attend the mandatory rehearsal.

Your convocation letter can be downloaded from the student portal.

Best regards,
Capital University of Science & Technology
"""

                # Send email
                email_message = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=settings.EMAIL_HOST_USER or "convocation@cust.edu.pk",
                    to=[student.email],
                )
                email_message.send()

                sent_emails.append(
                    {
                        "student_id": student.uu_id,
                        "student_name": student.name,
                        "email": student.email,
                        "status": "sent",
                    }
                )

            except Exception as e:
                errors.append(
                    {
                        "student_id": student.uu_id,
                        "student_name": student.name,
                        "email": student.email,
                        "error": str(e),
                    }
                )

        return Response(
            {
                "message": f"Sent {len(sent_emails)} convocation emails successfully",
                "sent_count": len(sent_emails),
                "error_count": len(errors),
                "sent_emails": sent_emails,
                "errors": errors[:10] if errors else [],
            },
            status=status.HTTP_200_OK,
        )
