# Generated by Django 4.2.3 on 2024-07-02 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_customer_subscription_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='subscription_reference',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
