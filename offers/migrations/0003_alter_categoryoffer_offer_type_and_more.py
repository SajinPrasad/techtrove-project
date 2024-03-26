# Generated by Django 5.0.2 on 2024-03-24 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0002_categoryoffer_offer_type_productoffer_offer_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryoffer',
            name='offer_type',
            field=models.CharField(choices=[('PRODUCT', 'Product offer'), ('CATEGORY', 'Category offer')], max_length=15),
        ),
        migrations.AlterField(
            model_name='productoffer',
            name='offer_type',
            field=models.CharField(choices=[('PRODUCT', 'Product offer'), ('CATEGORY', 'Category offer')], max_length=15),
        ),
    ]