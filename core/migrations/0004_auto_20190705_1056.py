# Generated by Django 2.2.1 on 2019-07-05 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190705_0034'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='chalenges_degree',
            new_name='challenge_degree',
        ),
    ]
