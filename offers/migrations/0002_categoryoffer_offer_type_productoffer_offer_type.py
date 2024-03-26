# Generated by Django 5.0.2 on 2024-03-24 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryoffer',
            name='offer_type',
            field=models.CharField(choices=[('PRODUCT', 'Product offer'), ('CATEGORY', 'Category offer')], default='offer', max_length=15),
        ),
        migrations.AddField(
            model_name='productoffer',
            name='offer_type',
            field=models.CharField(choices=[('PRODUCT', 'Product offer'), ('CATEGORY', 'Category offer')], default='offer', max_length=15),
        ),
    ]