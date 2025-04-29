from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from webpush import send_user_notification
def send_alert_email(to_email, subject, message, recipient_name="User", action_url=None):
    context = {
        "subject": subject,
        "message": message,
        "recipient_name": recipient_name,
        "action_url": action_url,
        "site_name": "CustApp",
        "support_email": "support@custapp.pk",
    }
    
    html_content = render_to_string("email/alert_email.html", context)
    text_content = f"{subject}\n\n{message}\n\nVisit: {action_url}" if action_url else f"{subject}\n\n{message}"

    email = EmailMultiAlternatives(subject, text_content, "support@custapp.pk", [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_comment_notification(self, user_type, name, text, employee, student):
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

