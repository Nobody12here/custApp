from rest_framework.permissions import  AllowAny
from rest_framework.viewsets import ModelViewSet
from ApplicationTemplate.models import Request
from .serializers import GuestPassRequestSerializer


class RequestGuestPassView(ModelViewSet):
    serializer_class = GuestPassRequestSerializer
    permission_classes = [AllowAny]
    queryset = Request.objects.filter(request_type="GuestPass").order_by("-created_at")
