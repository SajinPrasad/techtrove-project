# Generated by Django 5.0.2 on 2024-03-10 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0002_alter_coupon_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='userd_count',
            new_name='used_count',
        ),
    ]
