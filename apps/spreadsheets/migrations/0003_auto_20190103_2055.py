# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-03 20:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spreadsheets', '0002_auto_20190103_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spreadsheet',
            name='campaign',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='campaigns.Campaign'),
        ),
    ]
