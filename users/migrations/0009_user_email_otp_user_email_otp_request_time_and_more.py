# Generated by Django 4.2.3 on 2024-05-11 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_user_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_otp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='email_otp_request_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]