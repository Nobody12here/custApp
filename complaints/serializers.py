from ApplicationTemplate.models import Request
from rest_framework.serializers import ModelSerializer


class ComplaintSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = [
            "status",
            "request_type",
            "comments",
            "created_at",
            "complain_description",
            "complain_department_head",
            "applicant"
        ]
        
