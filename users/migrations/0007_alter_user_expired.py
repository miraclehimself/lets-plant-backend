# Generated by Django 4.2.3 on 2024-03-23 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_used_free_trial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='expired',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
