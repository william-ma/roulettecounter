# Generated by Django 2.1.5 on 2020-02-07 06:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulettecounter', '0005_auto_20200207_1722'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='dateEnd',
            new_name='date_end',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='dateStart',
            new_name='date_start',
        ),
        migrations.AlterField(
            model_name='number',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 7, 17, 35, 8, 480671)),
        ),
    ]