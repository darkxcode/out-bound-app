# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-02 17:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.PositiveSmallIntegerField()),
                ('column', models.PositiveSmallIntegerField()),
                ('content', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Cell',
                'verbose_name_plural': 'Cells',
            },
        ),
        migrations.CreateModel(
            name='Spreadsheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(help_text='Only <strong>.xls</strong> files are supported.', upload_to='spreadsheets')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spreadsheets', to='campaigns.Campaign')),
            ],
            options={
                'verbose_name': 'spreadsheet',
                'verbose_name_plural': 'spreadsheets',
            },
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_name', to='spreadsheets.Cell')),
                ('email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='email', to='spreadsheets.Cell')),
                ('first_name', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='first_name', to='spreadsheets.Cell')),
                ('last_name', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_name', to='spreadsheets.Cell')),
                ('snippet_1', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='snippet_1', to='spreadsheets.Cell')),
                ('snippet_2', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='snippet_2', to='spreadsheets.Cell')),
                ('snippet_3', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='snippet_3', to='spreadsheets.Cell')),
                ('spreadsheet', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='spreadsheets.Spreadsheet')),
            ],
            options={
                'verbose_name': 'Structure',
                'verbose_name_plural': 'Structures',
            },
        ),
        migrations.AddField(
            model_name='cell',
            name='spreadsheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cells', to='spreadsheets.Spreadsheet'),
        ),
    ]
