from django.db import models
from CUSTApp.models import Users, Department


# Create your models here.
class GuestPassRequest(models.Model):
    guest = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="guest"
    )
    host_department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="host"
    )
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    date_time = models.DateTimeField(name="date-time",blank=True,null=True)
    comments = models.TextField(null=True, blank=True)

    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "guest_pass_requests"

    def __str__(self):
        return f"Guest pass of {self.guest.name} "
