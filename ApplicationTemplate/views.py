from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ApplicationsSerializer
from .models import Applications
from rest_framework.permissions import IsAuthenticated

# Create your views here.


# Application Viewset
class ApplicationTemplateViewset(ModelViewSet):
    """
    This API provides CRUD functionality with The application model
    Note: The delete method doesnt delete the whole record, it just sets the disabled = true
    """

    serializer_class = ApplicationsSerializer
    queryset = Applications.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == "list":
            return Applications.objects.filter(status=1)
        return super().get_queryset()

    def perform_destroy(self, instance):
        instance.status = 0
        instance.save()
