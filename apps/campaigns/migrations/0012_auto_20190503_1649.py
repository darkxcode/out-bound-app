# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-03 16:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0011_auto_20190202_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipient',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
