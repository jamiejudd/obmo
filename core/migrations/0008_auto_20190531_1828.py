# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-05-31 17:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_balanceupdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commitment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('committed_value', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Revelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revealed_value', models.CharField(max_length=128)),
                ('commitment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Commitment')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='committed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='account',
            name='committed_value',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='key',
            field=models.DecimalField(decimal_places=999, max_digits=1000, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='linked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='account',
            name='registered_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='txn',
            name='txn_type',
            field=models.CharField(choices=[('Transfer', 'Transfer'), ('Commitment', 'Commitment'), ('Revealation', 'Revealation'), ('Registration', 'Registration'), ('ChangeVote', 'ChangeVote'), ('Challenge', 'Challenge'), ('ChangeChallengeVote', 'ChangeChallengeVote')], max_length=20),
        ),
        migrations.AddField(
            model_name='revelation',
            name='txn',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn'),
        ),
        migrations.AddField(
            model_name='commitment',
            name='txn',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn'),
        ),
    ]
