# Generated by Django 2.2.1 on 2019-07-10 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20190710_2223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challengecreation',
            name='challenge',
        ),
    ]