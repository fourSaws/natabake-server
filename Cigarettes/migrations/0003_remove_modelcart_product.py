# Generated by Django 4.0.6 on 2022-07-27 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Cigarettes', '0002_alter_modelcart_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelcart',
            name='product',
        ),
    ]
