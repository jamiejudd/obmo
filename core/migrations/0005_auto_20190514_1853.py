# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-05-14 17:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_account_running_balance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='running_balance',
            new_name='ubidue',
        ),
        migrations.RenameField(
            model_name='account',
            old_name='running_balance_last_updated',
            new_name='ubidue_last_updated',
        ),
    ]
