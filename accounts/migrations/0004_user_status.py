# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 11:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20170427_0442'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='account status'),
        ),
    ]
