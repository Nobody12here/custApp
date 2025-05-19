# your_app/management/commands/send_push.py

from django.core.management.base import BaseCommand
from push_notifications.models import GCMDevice
import json
class Command(BaseCommand):
    help = 'Send push notification to all registered devices'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, help='Notification title', required=True)
        parser.add_argument('--body', type=str, help='Notification body', required=True)
        parser.add_argument('--url', type=str, help='Optional click URL', default="")

    def handle(self, *args, **kwargs):
        title = str(kwargs.get('title') or '')
        body = str(kwargs.get('body') or '')
        url = kwargs.get('url')

        if not title or not body:
            self.stdout.write(self.style.ERROR("Both --title and --body are required."))
            return

        payload = {
            "title": title,
            "body": body,
        }
        print(body)
        extra = {}
        if url:
            extra["click_action"] = url

        devices = GCMDevice.objects.all()
        if not devices.exists():
            self.stdout.write(self.style.WARNING("No devices found."))
            return

        result = devices.send_message(
                None,
                extra=payload,
                content_available=True
            )

        self.stdout.write(self.style.SUCCESS(f"Notification sent to {devices.count()} device(s)."))
