# Generated by Django 4.2.13 on 2024-07-03 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productkey",
            name="is_used",
            field=models.BooleanField(default=False),
        ),
    ]