from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from ApplicationTemplate.models import Request
from CUSTApp.models import Users


class GuestPassRequestSerializer(ModelSerializer):
    CNIC = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    # For GET (read-only from related guest)
    guest_cnic = serializers.CharField(source="guest.CNIC", read_only=True)
    guest_name = serializers.CharField(source="guest.name", read_only=True)
    guest_phone = serializers.CharField(source="guest.phone_number", read_only=True)
    host_department_name = serializers.CharField(
        source="host.dept.dept_name", read_only=True
    )
    host_name = serializers.CharField(
        source="host.name", read_only=True
    )

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
        guest_cnic = validated_data.pop("CNIC")
        guest_name = validated_data.pop("name")
        guest_phone_no = validated_data.pop("phone_number")
        guest, created = Users.objects.get_or_create(
            CNIC=guest_cnic,
            defaults={
                "name": guest_name,
                "user_type": "Guest",
                "phone_number": guest_phone_no,
            },
        )
        validated_data["guest"] = guest
        validated_data["request_type"] = "GuestPass"
        return Request.objects.create(**validated_data)
