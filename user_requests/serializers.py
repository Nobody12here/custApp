from ApplicationTemplate.models import Request
from rest_framework import serializers


class ComplaintSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            "status",
            "request_type",
            "comments",
            "created_at",
            "complain_description",
            "complain_department_head",
            "applicant_name",
            "applicant",
            "request_id"
        ]
    def get_applicant_name(self,obj:Request):
        return obj.applicant.name if obj.applicant else None 
    def validate(self, data):
        print(data)
        if not data["complain_description"]:
            raise serializers.ValidationError("Complaint Description not provided")
        if not data["complain_department_head"]:
            raise serializers.ValidationError("Complaint Head not provided")
        if not data["applicant"]:
            raise serializers.ValidationError("Complaint applicant not provided")
        return data
