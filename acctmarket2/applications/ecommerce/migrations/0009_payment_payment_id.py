# Generated by Django 4.2.13 on 2024-08-06 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0008_delete_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="payment_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]