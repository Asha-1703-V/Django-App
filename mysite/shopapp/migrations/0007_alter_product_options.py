# Generated by Django 5.1.6 on 2025-02-24 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0006_order_products'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name', 'price']},
        ),
    ]
