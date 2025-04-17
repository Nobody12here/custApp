from rest_framework.response import Response
from rest_framework import status
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
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=1)  # Save with default status
        return Response(
            {"success": "Application Created Successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    def perform_destroy(self, instance):
        instance.status = 0
        instance.save()
       
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
        {"success": "Application Deleted Successfully"},
        status=status.HTTP_200_OK)
