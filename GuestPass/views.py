from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from ApplicationTemplate.models import Request
from .serializers import GuestPassRequestSerializer
from django.db.models import Case, When, Value, BooleanField
from datetime import date


class RequestGuestPassView(ModelViewSet):
    serializer_class = GuestPassRequestSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        today = date.today()

        # Annotate each request with whether its meeting date is today
        queryset = (
            Request.objects.filter(request_type="GuestPass")
            .annotate(
                is_today=Case(
                    When(meeting_date_time__date=today, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .order_by(
                "-is_today",  # Today's meetings first
                "meeting_date_time",  # Then sort by meeting time (earliest first)
                "-created_at",  # Finally by creation time (newest first)
            )
        )

        return queryset
