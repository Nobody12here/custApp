from django.db import models
from CUSTApp.models import Users, Department


# Create your models here.
class GuestPassRequest(models.Model):
    guest = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="guest_reqests"
    )
    host_department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="guest_pass_requests"
    )
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    date_time = models.DateTimeField(name="date-time")
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "guest_pass_requests"

    def __str__(self):
        return f"Guest pass of {self.guest.name} "
