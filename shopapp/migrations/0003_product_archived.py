# Generated by Django 4.1.6 on 2023-02-09 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0002_product_created_at_product_discount_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="archived",
            field=models.BooleanField(default=False),
        ),
    ]
