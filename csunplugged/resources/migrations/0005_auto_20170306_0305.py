# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-06 03:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0004_auto_20170226_0758'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resource',
            old_name='folder',
            new_name='generation_view',
        ),
        migrations.AddField(
            model_name='resource',
            name='webpage_template',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
