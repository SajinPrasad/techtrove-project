# Generated by Django 5.0.2 on 2024-03-24 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_category', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=600),
        ),
    ]
