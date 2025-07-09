from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import ComplaintSerializer
from ApplicationTemplate.serializers import RequestSerializer
from ApplicationTemplate.models import Request
from django.db.models import Q


class RequestViewset(ModelViewSet):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        request_type = self.request.query_params.get("type", "application")
        if request_type == "complaint":
            return ComplaintSerializer
        else:
            return RequestSerializer

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        request_type: str = self.request.query_params.get("type", "application")
        base_queryset = Request.objects.filter(request_type=request_type.capitalize())
        if user_type == "Student":
            base_queryset = base_queryset.filter(applicant=user)
        if user_type == "Staff":
            if request_type == "complaint":
                base_queryset = base_queryset.filter(
                    Q(EmployeeID=user.user_id) | Q(complain_department_head=user)
                )
            else:
                base_queryset = base_queryset.filter(EmployeeID=user.user_id)
        return base_queryset

    def perform_create(self, serializer):
        user = self.request.user
        department_head = self.request.data
        print(department_head)
        request_type: str = self.request.query_params.get("type", "application")

        serializer.validated_data["request_type"] = request_type.capitalize()
        if request_type == "complaint":
            serializer.validated_data.setdefault("status", "Pending")
        serializer.save()
