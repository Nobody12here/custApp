from rest_framework import serializers
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
    responsible_dept_id = serializers.IntegerField(source='application.responsible_dept.dept_id', read_only=True)
    responsible_dept_name = serializers.StringRelatedField(source='application.responsible_dept.dept_name', read_only=True)

    class Meta:
        model = Request
        fields = [
            'request_id', 'application', 'status', 'applicant', 'created_at', 'updated_at',
            'comments', 'payment_status', 'payment_date', 'EmployeeID', 'StudentID','responsible_dept_id','responsible_dept_name', 'renderedtemplate'
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

        return data

