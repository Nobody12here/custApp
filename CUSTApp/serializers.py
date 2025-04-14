# myapp/serializers.py
from rest_framework import serializers
from .models import Users, Department, Applications, Request, TemplateAttributes

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    dept_head_name = serializers.CharField(source='dept_head.name', read_only=True)
    class Meta:
        model = Department
        fields = '__all__'

# class ApplicationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Applications
#         fields = '__all__'

#     def validate(self, data):
#         if not data.get('application_name'):
#             raise serializers.ValidationError({"application_name": "This field cannot be empty."})
#         if not data.get('short_name'):
#             raise serializers.ValidationError({"short_name": "This field is required."})
#         if not data.get('application_desc'):
#             raise serializers.ValidationError({"application_desc": "This field is required."})
#         if data.get('status') not in [0, 1]:
#             raise serializers.ValidationError({"status": "Status must be 0 (Disabled) or 1 (Enabled)."})
#         if data.get('responsible_dept') is None:
#             raise serializers.ValidationError({"responsible_dept": "This field is required."})
#         if data.get('default_responsible_employee') is None:
#             raise serializers.ValidationError({"default_responsible_employee": "This field is required."})
#         return data

class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applications
        fields = '__all__'

    def validate(self, data):
        if not data.get('application_name'):
            raise serializers.ValidationError({"application_name": "This field cannot be empty."})
        if not data.get('short_name'):
            raise serializers.ValidationError({"short_name": "This field is required."})
        if not data.get('application_desc'):
            raise serializers.ValidationError({"application_desc": "This field is required."})
        if data.get('status') not in [0, 1]:
            raise serializers.ValidationError({"status": "Status must be 0 (Disabled) or 1 (Enabled)."})
        if data.get('responsible_dept') is None:
            raise serializers.ValidationError({"responsible_dept": "This field is required."})
        if data.get('default_responsible_employee') is None:
            raise serializers.ValidationError({"default_responsible_employee": "This field is required."})
        return data

class TemplateAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateAttributes
        fields = '__all__'

    def validate(self, data):
        if not data.get('attribute_name'):
            raise serializers.ValidationError({"attribute_name": "This field cannot be empty."})
        return data

# class TemplateAttributesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TemplateAttributes
#         fields = '__all__'

#     def validate(self, data):
#         if not data.get('attribute_name'):
#             raise serializers.ValidationError({"attribute_name": "This field cannot be empty."})
#         return data

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            'request_id', 'application', 'status', 'applicant', 'created_at', 'updated_at',
            'comments', 'payment_status', 'payment_date', 'EmployeeID', 'StudentID', 'renderedtemplate', 'request_file'
        ]
        read_only_fields = ['request_id', 'created_at', 'updated_at']  # Prevent manual override

    def validate(self, data):
        # Ensure required fields
        if not data.get('application'):
            raise serializers.ValidationError({"application": "This field is required."})
        if not data.get('applicant'):
            raise serializers.ValidationError({"applicant": "This field is required."})
        
        # Default values if not provided
        if not data.get('status'):
            data['status'] = 'Pending'
        if not data.get('payment_status'):
            data['payment_status'] = 'Pending'
        
        if not data.get('StudentID'):
            raise serializers.ValidationError({"StudentID": "This field is required."})
        
        # Validate file if provided (optional)
        request_file = data.get('request_file', None)
        if request_file:
            # Check the file type (optional, for example)
            if not request_file.name.endswith('.pdf'):  # Example: Only allow PDF files
                raise serializers.ValidationError({"request_file": "Only PDF files are allowed."})
            # Check file size (optional, for example: limit to 5MB)
            if request_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError({"request_file": "File size must be less than 5MB."})
        
        return data
# New serializers for OTP APIs

from rest_framework import serializers

class OTPSendSerializer(serializers.Serializer):  # Use Serializer instead of ModelSerializer
    email = serializers.EmailField()

    def validate_email(self, value):
        # Optional: Add custom validation if needed
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        if not otp:
            raise serializers.ValidationError({"otp": "This field is required."})
        return data
