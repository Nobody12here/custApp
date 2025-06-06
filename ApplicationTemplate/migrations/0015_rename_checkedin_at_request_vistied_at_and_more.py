# Generated by Django 4.1.13 on 2025-06-04 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ApplicationTemplate', '0014_request_checkedin_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='request',
            old_name='checkedin_at',
            new_name='vistied_at',
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Expired', 'Expired'), ('Visited', 'Visited')], default='Pending', max_length=50),
        ),
    ]
