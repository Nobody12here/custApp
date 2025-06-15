from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from ApplicationTemplate.models import Request
from .serializers import GuestPassRequestSerializer
from django.db.models import Case, When, Value, BooleanField
from django.utils import timezone
from datetime import datetime, timedelta
from push_notifications.models import GCMDevice
from firebase_admin import messaging


class RequestGuestPassView(ModelViewSet):
    serializer_class = GuestPassRequestSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Get today's date in the correct timezone
        user = self.request.user
        show_today = self.request.query_params.get("show_today", False)

        base_queryset = Request.objects.filter(request_type="GuestPass")
        now = timezone.now()
        today = now.date()

        # Compute start and end of today (timezone-aware)
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = start_of_day + timedelta(days=1)
        if user.is_authenticated:
            if (
                user.dept.dept_name == "Security"
                and user.dept.dept_head_id == user.user_id
            ):
                queryset = base_queryset
            else:
                queryset = base_queryset.filter(host=user.user_id)
        else:
            queryset = base_queryset
        queryset = (
            queryset.annotate(
                is_today=Case(
                    When(
                        meeting_date_time__gte=start_of_day,
                        meeting_date_time__lt=end_of_day,
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .order_by(
                "-is_today",  # Today's meetings first
                "-meeting_date_time",  # Then by meeting time (earliest first)
                "-created_at",  # Finally by creation time (newest first)
            )
            .exclude(status="Expired")
        )
        if show_today:
            queryset = queryset.filter(is_today=True)
        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_meeting_time = instance.meeting_date_time

        # Perform the update first
        response = super().partial_update(request, *args, **kwargs)

        # Check if meeting date/time was changed
        instance.refresh_from_db()
        if instance.meeting_date_time != old_meeting_time:
            self.send_update_notification(instance)

        return response

    def send_update_notification(self, request_instance):
        # Get the guest's mobile device
        guest_device = GCMDevice.objects.filter(user=request_instance.host).first()

        if not guest_device:
            return False

        # Format the meeting time for display
        meeting_time = request_instance.meeting_date_time.astimezone(
            timezone.get_current_timezone()
        ).strftime("%B %d, %Y at %I:%M %p")

        # Create the notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title="Meeting Time Updated",
                body=f"Your meeting time has been changed to {meeting_time}",
            ),
            data={
                "type": "meeting_update",
                "title": "Meeting Time Updated",
                "body": f"Your meeting time has been changed to {meeting_time}",
                "new_time": request_instance.meeting_date_time.isoformat(),
                "request_id": str(request_instance.request_id),
                "click_action": "FLUTTER_NOTIFICATION_CLICK",  # Remove if not using Flutter
            },
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="meeting_updates", sound="default"
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                    ),
                ),
            ),
        )

        try:
            guest_device.send_message(message)
            return True
        except Exception as e:
            # You might want to log this error
            print(f"Failed to send notification: {str(e)}")
            return False
