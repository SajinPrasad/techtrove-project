# Generated by Django 5.0.2 on 2024-03-03 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_order_total_alter_order_tax'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed'), ('Refunded', 'Refunded'), ('Processing', 'Processing'), ('Cancelled', 'Cancelled')], default='Pending', max_length=15),
        ),
    ]
