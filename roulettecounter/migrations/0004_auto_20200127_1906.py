# Generated by Django 2.1.5 on 2020-01-27 08:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulettecounter', '0003_number_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='number',
            name='count',
        ),
        migrations.AlterField(
            model_name='number',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 27, 19, 6, 50, 511262)),
        ),
    ]