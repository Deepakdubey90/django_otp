# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-13 03:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20170412_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='userconfirmationcode',
            name='is_used',
            field=models.BooleanField(default=False, verbose_name='Used ?'),
        ),
    ]