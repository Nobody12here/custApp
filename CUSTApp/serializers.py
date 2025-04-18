# myapp/serializers.py
from rest_framework import serializers

from ApplicationTemplate.models import Request
from .models import Users, Department, TemplateAttributes,Program
import json
class UsersSerializer(serializers.ModelSerializer):
    DoB = serializers.DateField(input_formats=["%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y"])
    class Meta:
        model = Users
        exclude = ['password']  # Exclude password field from serialization
        

class DepartmentSerializer(serializers.ModelSerializer):
    dept_head_name = serializers.CharField(source='dept_head.name', read_only=True)
    programs = serializers.SerializerMethodField()
    class Meta:
        model = Department
        fields = '__all__'
    def get_programs(self,obj):
        programs = obj.program_set.all()
        return ProgramSerializer(programs, many=True).data

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

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

    
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
            'comments', 'payment_status', 'payment_date', 'EmployeeID', 'StudentID', 'renderedtemplate','request_file', 
        ]
        read_only_fields = ['request_id', 'created_at', 'updated_at']  # Prevent manual override

    def to_representation(self, instance):
        """
        Convert comments to a JSON array when serializing.
        If comments is a string, parse it; if null, return an empty list.
        """
        representation = super().to_representation(instance)
        if instance.comments:
            try:
                # If comments is stored as a JSON string, parse it
                representation['comments'] = json.loads(instance.comments) if isinstance(instance.comments, str) else instance.comments
            except json.JSONDecodeError:
                representation['comments'] = []
        else:
            representation['comments'] = []
        return representation

    def to_internal_value(self, data):
        """
        Ensure comments is stored as a JSON string when deserializing.
        Validate that comments is a list of valid comment objects.
        """
        # Make a mutable copy if needed
        data_copy = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Process the comments field separately
        raw_comments = data_copy.pop("comments", []) if "comments" in data_copy else []
        
        # If raw_comments is already a string (like when it comes from parsed JSON in request body)
        if isinstance(raw_comments, str):
            try:
                # Try to parse it as JSON
                parsed_comments = json.loads(raw_comments)
                raw_comments = parsed_comments
            except json.JSONDecodeError:
                raise serializers.ValidationError({"comments": "Invalid JSON format"})
        
        # Now raw_comments should be a list (empty or with comment objects)
        if raw_comments:
            if isinstance(raw_comments, list):
                for comment in raw_comments:
                    if not isinstance(comment, dict):
                        raise serializers.ValidationError({"comments": "Each comment must be an object."})
                    required_fields = {'name', 'text', 'type', 'timestamp'}
                    if not all(field in comment for field in required_fields):
                        raise serializers.ValidationError({
                            "comments": f"Each comment must contain: {', '.join(required_fields)}"
                        })
                    if comment["type"] not in ["student", "admin"]:
                        raise serializers.ValidationError({
                            "comments": "Comment type must be 'student' or 'admin'."
                        })
                comments_json = json.dumps(raw_comments)
            else:
                raise serializers.ValidationError({"comments": "Comments must be a list of objects"})
        else:
            comments_json = '[]'
        
        # Process the rest of the fields normally
        validated_data = super().to_internal_value(data_copy)
        validated_data["comments"] = comments_json
        return validated_data

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
