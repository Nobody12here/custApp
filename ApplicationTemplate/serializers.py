from rest_framework import serializers
import json
from .models import Applications,Request

class ApplicationsSerializer(serializers.ModelSerializer):
    default_responsible_employee_name = serializers.CharField(source='default_responsible_employee.name', read_only=True)
    dept_name = serializers.CharField(source='responsible_dept.dept_name', read_only=True)
    class Meta:
        model = Applications
        fields = '__all__'
        extra_fields = ['default_responsible_employee_name', 'dept_name']

    def validate(self, data):
        request_method = self.context.get('request').method if self.context.get('request') else None
        if request_method != 'PATCH':
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


class RequestSerializer(serializers.ModelSerializer):
    responsible_dept_id = serializers.IntegerField(
        source="application.responsible_dept.dept_id", read_only=True
    )
    responsible_dept_name = serializers.StringRelatedField(
        source="application.responsible_dept.dept_name", read_only=True
    )
    responsible_employee_name = serializers.StringRelatedField(
        source="application.default_responsible_employee.name"
    )
    responsible_employee_designation = serializers.StringRelatedField(
        source="application.default_responsible_employee.designation"
    )
    responsible_employee_signature = serializers.StringRelatedField(
        source="application.default_responsible_employee.signature"
    )
    student_name = serializers.StringRelatedField(source="applicant.name")
    application_name = serializers.StringRelatedField(
        source="application.application_name"
    )


    class Meta:
        model = Request
        fields = [
            "responsible_employee_signature",
            "request_id",
            "application",
            "application_name",
            "status",
            "applicant",
            "created_at",
            "updated_at",
            "approved_at",
            "comments",
            "payment_status",
            "payment_date",
            "EmployeeID",
            "StudentID",
            "student_name",
            "renderedtemplate",
            "responsible_dept_id",
            "responsible_dept_name",
            "responsible_employee_name",
            "request_file",
            "request_type",
            "responsible_employee_designation",
        ]
        read_only_fields = [
            "request_id",
        ]  # Prevent manual override

    def to_representation(self, instance):
        """
        Convert comments to a JSON array when serializing.
        If comments is a string, parse it; if null, return an empty list.
        """
        representation = super().to_representation(instance)
        if instance.comments:
            try:
                # If comments is stored as a JSON string, parse it
                representation["comments"] = (
                    json.loads(instance.comments)
                    if isinstance(instance.comments, str)
                    else instance.comments
                )
            except json.JSONDecodeError:
                representation["comments"] = []
        else:
            representation["comments"] = []
        return representation

    def to_internal_value(self, data):
        """
        Ensure comments is stored as a JSON string when deserializing.
        Validate that comments is a list of valid comment objects.
        """
        # Make a mutable copy if needed
        data_copy = data.copy() if hasattr(data, "copy") else dict(data)

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
                        raise serializers.ValidationError(
                            {"comments": "Each comment must be an object."}
                        )
                    required_fields = {"name", "text", "type", "timestamp"}
                    if not all(field in comment for field in required_fields):
                        raise serializers.ValidationError(
                            {
                                "comments": f"Each comment must contain: {', '.join(required_fields)}"
                            }
                        )
                    if comment["type"] not in ["Student", "admin", "Staff"]:
                        raise serializers.ValidationError(
                            {"comments": "Comment type must be 'student' or 'admin'."}
                        )
                comments_json = json.dumps(raw_comments)
            else:
                raise serializers.ValidationError(
                    {"comments": "Comments must be a list of objects"}
                )
        else:
            comments_json = "[]"

        # Process the rest of the fields normally
        validated_data = super().to_internal_value(data_copy)
        validated_data["comments"] = comments_json
        return validated_data

    def validate(self, data):
        # Ensure required fields
        if not data.get("application"):
            raise serializers.ValidationError(
                {"application": "This field is required."}
            )
        if not data.get("applicant"):
            raise serializers.ValidationError({"applicant": "This field is required."})

        # Default values if not provided
        if not data.get("status"):
            data["status"] = "Pending"
        if not data.get("payment_status"):
            data["payment_status"] = "Pending"

        if not data.get("StudentID"):
            raise serializers.ValidationError({"StudentID": "This field is required."})

        return data

