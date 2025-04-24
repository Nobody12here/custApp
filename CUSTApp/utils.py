from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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

    email = EmailMultiAlternatives(subject, text_content, "no-reply@mysite.com", [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
