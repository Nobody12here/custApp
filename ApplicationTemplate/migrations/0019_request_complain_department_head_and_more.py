# Generated by Django 4.1.13 on 2025-07-07 06:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ApplicationTemplate', '0018_remove_request_guest_fcm_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='complain_department_head',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='handled_complaints', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='complain_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_type',
            field=models.CharField(choices=[('GuestPass', 'GuestPass'), ('Application', 'Application'), ('Complaint', 'Complaint')], default='Application', max_length=50),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Expired', 'Expired'), ('Resolved', 'Resolved'), ('Visited', 'Visited')], default='Pending', max_length=50),
        ),
    ]
