# Generated by Django 4.2.3 on 2024-08-06 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processplant', '0006_processplant_soil_type_processplant_sun_frequency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='processplant',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='processplant',
            name='rate',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='processplant',
            name='rated',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
