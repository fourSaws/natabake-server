# Generated by Django 4.1.1 on 2022-11-21 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Cigarettes", "0003_modelproduct_show"),
    ]

    operations = [
        migrations.AlterField(
            model_name="modelproduct",
            name="show",
            field=models.BooleanField(blank=True, default=True, verbose_name="Показывать"),
        ),
    ]
