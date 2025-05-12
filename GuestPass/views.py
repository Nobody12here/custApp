from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from .serializers import GuestPassRequestSerializer,GuestPassRequest


class RequestGuestPassView(ModelViewSet):
    serializer_class = GuestPassRequestSerializer
    permission_classes = [AllowAny]
    queryset = GuestPassRequest.objects.all()
    