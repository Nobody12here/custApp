from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from ApplicationTemplate.models import Request
from CUSTApp.models import Users
from CUSTApp.utils import (
    send_alert_email,
)  # Import your existing notification functions


class GuestPassRequestSerializer(ModelSerializer):
    CNIC = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    guest_fcm_token = serializers.CharField(
        write_only=True, required=False, allow_null=True, allow_blank=True
    )

    # For reading the token (if needed)
    guest_token = serializers.CharField(source="guest.fcm_token", read_only=True)

    # For GET (read-only from related guest)
    guest_cnic = serializers.CharField(source="guest.CNIC", read_only=True)
    guest_name = serializers.CharField(source="guest.name", read_only=True)
    guest_phone = serializers.CharField(source="guest.phone_number", read_only=True)
    host_department_name = serializers.CharField(
        source="host.dept.dept_name", read_only=True
    )
    host_name = serializers.CharField(source="host.name", read_only=True)

    class Meta:
        model = Request
        fields = [
            "guest",
            "host",
            "status",
            "created_at",
            "request_id",
            "reason",
            "status",
            "request_type",
            "meeting_date_time",
            "comments",
            "CNIC",
            "name",
            "phone_number",
            "host_name",
            "host_department_name",
            "guest_phone",
            "guest_name",
            "guest_fcm_token",
            "guest_token",
            "guest_cnic",
        ]
        read_only_fields = ["guest", "created_at"]
        extra_kwargs = {
            "guest_cnic_read": {"read_only": True},
            "guest_name_read": {"read_only": True},
            "guest_phone_read": {"read_only": True},
            "host_name": {"read_only": True},
            "host_department_name": {"read_only": True},
        }

    def create(self, validated_data):
        # First check if the user with the given CNIC exists or not
        guest_cnic = validated_data.pop("CNIC").replace("-", "")  # Remove hyphens from CNIC
        guest_name = validated_data.pop("name")
        guest_phone_no = validated_data.pop("phone_number")
        guest_fcm_token = validated_data.pop("guest_fcm_token", None)

        # Get host information before creating the request
        host = validated_data.get("host")
        guest, created = Users.objects.update_or_create(
            CNIC=guest_cnic,
            defaults={
                "name": guest_name,
                "user_type": "Guest",
                "phone_number": guest_phone_no,
                "guest_fcm_token": guest_fcm_token if guest_fcm_token else None,
            },
        )
        print(guest_fcm_token, guest.guest_fcm_token)
        # Update FCM token if provided (even for existing guests)
        if (guest_fcm_token) and (guest.guest_fcm_token != guest_fcm_token):
            guest.guest_fcm_token = guest_fcm_token
            guest.save(update_fields=["guest_fcm_token"])
            print("FCM token updated for guest:", guest.name)
        validated_data["guest"] = guest
        validated_data["request_type"] = "GuestPass"

        # Create the request
        request = Request.objects.create(**validated_data)

        # Send notifications to host
        self.send_new_request_notifications(request, host, guest)

        return request

    def send_new_request_notifications(self, request, host, guest=None):
        """Send both email and push notification for new guest pass request"""
        try:
            # Prepare common notification details
            visit_datetime = request.meeting_date_time
            formatted_date = visit_datetime.strftime("%B %d, %Y")
            formatted_time = visit_datetime.strftime("%I:%M %p")

            subject = f"New Guest Pass Request: {request.guest.name}"
            message = (
                f"You have a new guest pass request from {request.guest.name}.\n"
                f"Visit Date: {formatted_date}\n"
                f"Visit Time: {formatted_time}\n"
                f"Purpose: {request.reason}"
            )

            action_url = f"https://custapp.pk/guest-passes/{request.request_id}/"

            # Send email notification
            send_alert_email(
                to_email=host.email,
                subject=subject,
                message=message,
                recipient_name=host.name,
                action_url=action_url,
            )
            

        except Exception as e:
            # Log the error but don't prevent the request from being created
            print(f"Failed to send notifications: {str(e)}")
