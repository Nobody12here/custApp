from django.db import models

from django.core.validators import MinLengthValidator

# otp = models.CharField(
#     max_length=6, 
#     null=True, 
#     blank=True,
#     validators=[MinLengthValidator(6)]  # Ensure 6-digit OTP
# )


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    uu_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    program_name = models.CharField(max_length=255, null=True, blank=True)
    dept_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_type = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    picture = models.CharField(max_length=255, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    term = models.CharField(max_length=10, null=True, blank=True)
    DoB = models.DateField(null=True, blank=True)
    CNIC = models.CharField(max_length=15, null=True, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name

class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=255)
    dept_head = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='dept_head_id')
    short_name = models.CharField(max_length=100)  # Added to match schema

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.dept_name

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



class TemplateAttributes(models.Model):
    id = models.AutoField(primary_key=True)
    attribute_name = models.CharField(max_length=255)
    attribute_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True, related_name='attributes')

    class Meta:
        db_table = 'template_attributes'

    def __str__(self):
        return self.attribute_name
    
class Request(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    request_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='application_id')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    applicant = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='applicant_id')
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    updated_at = models.DateTimeField(auto_now=True)      # Auto-set on update
    comments = models.TextField(null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    EmployeeID = models.IntegerField(null=True, blank=True)  # Added to match DB
    StudentID = models.IntegerField(null=True, blank=True)   # Added to match DB
    renderedtemplate = models.CharField(max_length=10000, null=True, blank=True)  # Added to match DB
    request_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    class Meta:
        db_table = 'request'

    def __str__(self):
        return f"Request {self.request_id} - {self.application}"
