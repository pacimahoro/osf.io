# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-09 16:01
from __future__ import unicode_literals

from django.db import migrations, models
import osf.utils.datetime_aware_jsonfield


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0023_auto_20161208_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodelicenserecord',
            name='year',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='preprintprovider',
            name='subjects_acceptable',
            field=osf.utils.datetime_aware_jsonfield.DateTimeAwareJSONField(blank=True, default=list),
        ),
    ]
