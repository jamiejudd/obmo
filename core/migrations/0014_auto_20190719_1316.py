# Generated by Django 2.2.1 on 2019-07-19 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_challengecreation_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='good',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='challenge',
            name='good',
            field=models.BooleanField(default=True),
        ),
    ]