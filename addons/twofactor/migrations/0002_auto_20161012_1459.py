# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-12 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import osf.models.base


class Migration(migrations.Migration):

    dependencies = [
        ('twofactor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactorusersettings',
            name='_id',
            field=models.CharField(db_index=True, default=osf.models.base.generate_object_id, max_length=24, unique=True),
        ),
    ]