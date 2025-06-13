from django.db import models
from CUSTApp.models import Users,Department
from django.core.validators import FileExtensionValidator
# Create your models here.
class Applications(models.Model):
    STATUS_CHOICES = [
        (1, 'Enabled'),
        (0, 'Disabled'),
    ]

    id = models.AutoField(primary_key=True)
    application_name = models.CharField(max_length=255)  # Template name
    short_name = models.CharField(max_length=100)  # Short name for application
    application_desc = models.TextField()  # Template content with placeholders
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)  # Enabled/Disabled
    responsible_dept = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='responsible_dept_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    default_responsible_employee = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        db_column='default_responsible_employee_id',
        default=1
    )

    class Meta:
        db_table = 'applications'

    def __str__(self):
        return self.application_name
class Request(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
        ('Visited', 'Visited'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    request_id = models.AutoField(primary_key=True)
    #GuestPass fields
    guest = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="guest_reqests",null=True,blank=True
    )
    host = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="host",null=True
    )
    reason = models.TextField(null=True)
    date_time = models.DateTimeField(name="meeting_date_time",blank=True,null=True)
    request_type = models.CharField(max_length=50, choices=[('GuestPass', 'Application')], default='Application')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_id',blank=True,null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    applicant = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='applicant_id',blank=True,null=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)  # Auto-set on creation
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True,blank=True)      # Auto-set on update
    vistied_at = models.DateTimeField(null=True,blank=True)
    expired_at = models.DateTimeField(null=True,blank=True)
    comments = models.TextField(null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    EmployeeID = models.IntegerField(null=True, blank=True)  # Added to match DB
    StudentID = models.IntegerField(null=True, blank=True)   # Added to match DB
    request_file = models.FileField(
        upload_to="media/",null=True,blank=True,validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    renderedtemplate = models.CharField(max_length=10000, null=True, blank=True)  # Added to match DB

    class Meta:
        db_table = 'request'

    def __str__(self):
        return f"Request {self.request_id} - {self.application}"

