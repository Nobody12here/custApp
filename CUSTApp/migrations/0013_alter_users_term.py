# Generated by Django 4.1.13 on 2025-06-10 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CUSTApp', '0012_users_auth_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='term',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
