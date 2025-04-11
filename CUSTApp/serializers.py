# myapp/serializers.py
from rest_framework import serializers
from .models import Users, Department, TemplateAttributes

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
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
