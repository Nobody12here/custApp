from django.core.management.base import BaseCommand
from ApplicationTemplate.models import Request
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        # Compute start and end of today (timezone-aware)
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = start_of_day + timedelta(days=1)
        updated_count = Request.objects.filter(
            request_type="GuestPass",
            meeting_date_time__gte=start_of_day,
            meeting_date_time__lt=end_of_day,
        ).update(status="Expired")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully expired {updated_count} GuestPass requests"
            )
        )
