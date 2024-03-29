# Generated by Django 5.0.2 on 2024-03-10 11:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')], max_length=20)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('minimum_order_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('valid_from', models.DateField(blank=True, null=True)),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('applies_to_all_users', models.BooleanField(default=False)),
                ('max_usage_count', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('userd_count', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
