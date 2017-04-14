# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 09:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserConfirmationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmation_code', models.CharField(max_length=255, verbose_name='Confirmation Code')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.UserDataTable')),
            ],
        ),
    ]
