from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from webpush import send_user_notification
import json
from rest_framework.response import Response
from rest_framework import status


def send_alert_email(
    to_email, subject, message, recipient_name="User", action_url=None
):
    context = {
        "subject": subject,
        "message": message,
        "recipient_name": recipient_name,
        "action_url": action_url,
        "site_name": "CustApp",
        "support_email": "support@custapp.pk",
    }

    html_content = render_to_string("email/alert_email.html", context)
    text_content = (
        f"{subject}\n\n{message}\n\nVisit: {action_url}"
        if action_url
        else f"{subject}\n\n{message}"
    )

    email = EmailMultiAlternatives(
        subject, text_content, "support@custapp.pk", [to_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def add_comment_to_instance(request, instance):
    try:
        text = request.text
        if not text:
            return Response(
                {"error": "Comment text is required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        name = request.user.name
        user_type = request.user.user_type
        try:
            comments = (
                json.loads(instance.comments) if instance.comments else []
            )  # Load previous comment if exists
        except Exception:
            comments = []
        new_comment = {
            "name": name,
            "text": text,
            "user_type": user_type,
            "timestamp": timezone.now().isoformat(),
        }
        comments.append(new_comment)
        instance.comments = json.dumps(comments)
        instance.save
        return Response({"message": ""})
    except:
        return Response(
            {"error": "Some error occured!"}, status=status.HTTP_400_BAD_REQUEST
        )


def send_comment_notification(user_type, name, text, employee, student):
    payload = {
        "head": "New Comment",
        "body": f"{name} commented: {text}",
    }
    if user_type == "Student":
        send_user_notification(employee, payload=payload, ttl=1000)
        send_alert_email(
            employee.email,
            "New Comment on Your Application",
            f"{name} commented: {text}",
            recipient_name=employee.name,
            action_url=f"/user/dashboard/",
        )
    elif user_type == "Staff":
        send_alert_email(
            student.email,
            "New Comment on Your Application",
            f"{name} commented: {text}",
            recipient_name=student.name,
        )
