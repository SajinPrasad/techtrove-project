# Generated by Django 5.0.2 on 2024-04-05 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_variation_variation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('storage size', 'storage size'), ('screen size', 'screen size')], max_length=100),
        ),
    ]