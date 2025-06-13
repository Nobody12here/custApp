# your_app/management/commands/send_push.py

from django.core.management.base import BaseCommand
from push_notifications.models import GCMDevice
from firebase_admin import messaging


class Command(BaseCommand):
    help = "Send push notification to all registered devices"

    def add_arguments(self, parser):
        parser.add_argument(
            "--title", type=str, help="Notification title", required=True
        )
        parser.add_argument("--body", type=str, help="Notification body", required=True)
        parser.add_argument("--url", type=str, help="Optional click URL", default="")

    def handle(self, *args, **kwargs):
        title = str(kwargs.get("title") or "")
        body = str(kwargs.get("body") or "")
        url = kwargs.get("url") or "/"
        
        if not title or not body:
            self.stdout.write(self.style.ERROR("Both --title and --body are required."))
            return
            
        devices = GCMDevice.objects.filter(active=True)
        if not devices.exists():
            self.stdout.write(self.style.WARNING("No devices found."))
            return

        # Create a proper FCM message with both notification and data payloads
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                "title": title,
                "body": body,
                "url": url,
                "click_action": "FLUTTER_NOTIFICATION_CLICK"  # For Flutter apps
            },
            # For Android specific configurations
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='your_channel_id',  # Required for Android 8+
                    click_action="FLUTTER_NOTIFICATION_CLICK",
                    sound='default'
                ),
            ),
            # For iOS specific configurations
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
        )

        try:
            result = devices.send_message(message)
            self.stdout.write(self.style.SUCCESS(f"Notification sent to {devices.count()} device(s)."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send notification: {str(e)}"))