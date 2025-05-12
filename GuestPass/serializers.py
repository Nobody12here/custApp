from rest_framework.serializers import ModelSerializer
from .models import GuestPassRequest


class GuestPassRequestSerializer(ModelSerializer):
    class Meta:
        model = GuestPassRequest
        fields = "__all__"
