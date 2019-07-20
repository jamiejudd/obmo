# Generated by Django 2.2.1 on 2019-07-16 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_message'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arrow',
            old_name='expired',
            new_name='cancelled',
        ),
        migrations.AddField(
            model_name='challenge',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='challengelink',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='challengelink',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]
