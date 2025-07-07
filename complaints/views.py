from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ApplicationTemplate.models import Request
from .serializers import ComplaintSerializer
# Create your views here.


class ComplaintViewset(ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Request.objects.filter(request_type="Complaint")
