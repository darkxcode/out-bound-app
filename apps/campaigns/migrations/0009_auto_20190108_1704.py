# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-08 17:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0008_auto_20190108_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipient',
            name='spreadsheet',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='spreadsheets.Spreadsheet'),
        ),
    ]
