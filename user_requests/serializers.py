from ApplicationTemplate.models import Request
from rest_framework import serializers


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            "status",
            "request_type",
            "comments",
            "created_at",
            "complain_description",
            "complain_department_head",
            "applicant",
        ]

    def validate(self, data):
        if not data["complain_description"]:
            raise serializers.ValidationError("Complaint Description not provided")
        if not data["complain_department_head"]:
            raise serializers.ValidationError("Complaint Head not provided")
        if not data["applicant"]:
            raise serializers.ValidationError("Complaint applicant not provided")
        return data
