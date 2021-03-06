# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-12 19:24
from __future__ import unicode_literals

from django.db import migrations
import osf.models.validators
import osf.utils.datetime_aware_jsonfield


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0023_auto_20161212_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileversion',
            name='location',
            field=osf.utils.datetime_aware_jsonfield.DateTimeAwareJSONField(blank=True, db_index=True, default=dict, null=True, validators=[osf.models.validators.validate_location]),
        ),
        migrations.AlterIndexTogether(
            name='fileversion',
            index_together=set([]),
        ),
    ]
