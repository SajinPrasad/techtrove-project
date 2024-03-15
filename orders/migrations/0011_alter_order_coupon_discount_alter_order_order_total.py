# Generated by Django 5.0.2 on 2024-03-11 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_coupon_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='coupon_discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_total',
            field=models.DecimalField(decimal_places=2, max_digits=16),
        ),
    ]
