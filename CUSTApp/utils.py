from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from firebase_admin import messaging
import json
from .models import Users
from rest_framework.response import Response
from rest_framework import status


def notify_user_devices(user: Users, title, body, url=None):
    guest_fcm_token = user.guest_fcm_token
    if not guest_fcm_token:
        return False  # or you might want to raise an exception

    # Default URL if none provided
    url = url or "/"

    # Create a full-featured FCM message
    message = messaging.Message(
        token=guest_fcm_token,
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            "title": title,
            "body": body,
            "click_action": "FLUTTER_NOTIFICATION_CLICK",  # Remove if not using Flutter
        },
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                channel_id="your_default_channel",  # Required for Android 8+
                click_action="FLUTTER_NOTIFICATION_CLICK",  # Remove if not using Flutter
                sound="default",
                icon="notification_icon",  # Your app's notification icon
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default",
                    badge=1,
                ),
                headers={
                    "apns-priority": "10"  # Immediate delivery for iOS
                },
            ),
        ),
    )

    try:
        response = messaging.send(message)
        return True
    except Exception as e:
        # Log the error for debugging
        print(f"Failed to send notification: {str(e)}")
        return False


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
    email.connection = None
    email.send(fail_silently=False)


def add_comment_to_instance(request, instance, employee=None, student=None):
    try:
        text = request.data.get("text")
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
            "timestamp": datetime.now().isoformat(),
        }
        comments.append(new_comment)
        instance.comments = json.dumps(comments)
        instance.save()
        if employee and student:
            send_comment_notification(
                name=name,
                user_type=user_type,
                text=text,
                employee=employee,
                student=student,
            )
        return Response(
            {"message": "Saved sucessfully", "success": True},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response(
            {"error": "Some error occured!", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


def send_comment_notification(user_type, name, text, employee, student):
    #  = {
    #   payload  "head": "New Comment",
    #     "body": f"{name} commented: {text}",
    # }
    if user_type == "Student":
        # notify_user_devices(employee, "New comment on your applicaiton", body="You a new comment in your application!")
        send_alert_email(
            employee.email,
            "New Comment on Your Application",
            f"{name} commented: {text}",
            recipient_name=employee.name,
            action_url="/user/dashboard/",
        )
        notify_user_devices(
            employee, "New comment on your Application", f"{name} commented: {text}"
        )

    elif user_type == "Staff":
        send_alert_email(
            student.email,
            "New Comment on Your Application",
            f"{name} commented: {text}",
            recipient_name=student.name,
        )
        notify_user_devices(
            student, "New comment on your Application", f"{name} commented: {text}"
        )


def extract_year_term(reg_no: str) -> str:
    year_prefix = reg_no[:2]
    term_code = reg_no[2]
    term_map = {"1": "Spring", "3": "Fall"}
    year = f"20{year_prefix}"
    term = term_map.get(term_code, "Undefined Term Code")

    return f"{term} {year}"
