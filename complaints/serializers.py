from ApplicationTemplate.models import Request
from rest_framework.serializers import ModelSerializer

class ComplaintSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = ['status','request_type']