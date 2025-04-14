# CUSTApp/migrations/0005_delete_applications_and_requests.py

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('CUSTApp', '0004_remove_request_applicant_remove_request_application_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # No DB change
            state_operations=[
                migrations.DeleteModel(name='Applications'),
                migrations.DeleteModel(name='Request'),
            ]
        ),
    ]
