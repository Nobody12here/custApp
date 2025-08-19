# myapp/serializers.py
from rest_framework import serializers
from .models import Users, Department, TemplateAttributes, Program,Convocation

class ConvocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convocation
        exclude = ['created_at','updated_at']
    def create(self, validated_data):
        convocation = Convocation.objects.create(**validated_data)
        convocation.save()
        return convocation
class ConvocationStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields=["name","email","uu_id","convocation"]

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        exclude = ["password"]  # Exclude password field from serialization


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "name",
            "picture",
            "signature",
            "CNIC",
            "phone_number",
            "dept",
            "program_name",
            "DoB",
        ]


class UserStudentDataUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["name", "father_name", "term", "CGPA", "uu_id", "gender"]


class DepartmentSerializer(serializers.ModelSerializer):
    dept_head_name = serializers.CharField(source="dept_head.name", read_only=True)
    programs = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = "__all__"

    def get_programs(self, obj):
        programs = obj.program_set.all()
        return ProgramSerializer(programs, many=True).data


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"


class TemplateAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateAttributes
        fields = "__all__"

    def validate(self, data):
        if not data.get("attribute_name"):
            raise serializers.ValidationError(
                {"attribute_name": "This field cannot be empty."}
            )
        return data


class OTPSendSerializer(
    serializers.Serializer
):  # Use Serializer instead of ModelSerializer
    email = serializers.EmailField()

    def validate_email(self, value):
        # Optional: Add custom validation if needed
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value


class PhoneOTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    otp = serializers.CharField(max_length=10)


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        if not otp:
            raise serializers.ValidationError({"otp": "This field is required."})
        return data
