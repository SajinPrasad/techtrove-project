# Generated by Django 5.0.2 on 2024-04-02 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='product_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
