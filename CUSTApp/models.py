from django.db import models

from django.core.validators import MinLengthValidator

# otp = models.CharField(
#     max_length=6, 
#     null=True, 
#     blank=True,
#     validators=[MinLengthValidator(6)]  # Ensure 6-digit OTP
# )


from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

# otp = models.CharField(
#     max_length=6, 
#     null=True, 
#     blank=True,
#     validators=[MinLengthValidator(6)]  # Ensure 6-digit OTP
# )

class UserManager(BaseUserManager):
    def create_user(self,email,name,**extra_fields):
        if not email:
            raise ValueError("Email Not provided")
        email = self.normalize_email(email)
        user= self.model(email=email,name=name,**extra_fields)
        user.set_unusable_password()
        user.save(using=self.db)
        return user
    def create_superuser(self,email,name,password=None,**extra_fields):
        if password==None:
            raise ValueError("Password is required to create superuser")
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)  # Set actual password for superuser
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser,PermissionsMixin):
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

    # Required for AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
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
class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)  # Added to match schema
    dept_id = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='dept_id')

    class Meta:
        db_table = 'program'

    def __str__(self):
        return self.program_name

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
    
