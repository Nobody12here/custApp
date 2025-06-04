from CUSTApp.utils import send_alert_email
from django.core.management.base import BaseCommand

import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        return send_alert_email(
            "uraja01313@gmail.com",
            "Cron JOB message",
            f"This email is sent through cron job at {datetime.datetime.now()}",
            "Muhammad Auzair",
        )
