from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from ApplicationTemplate.models import Request
from .serializers import GuestPassRequestSerializer
from django.db.models import Case, When, Value, BooleanField
from django.utils import timezone
from datetime import datetime, timedelta


class RequestGuestPassView(ModelViewSet):
    serializer_class = GuestPassRequestSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Get today's date in the correct timezone
        user = self.request.user
        show_today = self.request.query_params.get("show_today", False)

        base_queryset = Request.objects.filter(request_type="GuestPass")
        now = timezone.now()
        today = now.date()

        # Compute start and end of today (timezone-aware)
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = start_of_day + timedelta(days=1)
        if user.is_authenticated:
            if (
                user.dept.dept_name == "Security"
                and user.dept.dept_head_id == user.user_id
            ):
                # That means that the user is the head of security department
                print("head of security")
                queryset = base_queryset
            else:
                queryset = base_queryset.filter(host=user.user_id)
        else:
            queryset = base_queryset
        queryset = queryset.annotate(
            is_today=Case(
                When(
                    meeting_date_time__gte=start_of_day,
                    meeting_date_time__lt=end_of_day,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by(
            "-is_today",  # Today's meetings first
            "meeting_date_time",  # Then by meeting time (earliest first)
            "-created_at",  # Finally by creation time (newest first)
        )
        if show_today:
            queryset = queryset.filter(is_today=True)
        return queryset
