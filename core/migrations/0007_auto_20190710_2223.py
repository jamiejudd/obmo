# Generated by Django 2.2.1 on 2019-07-10 21:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20190709_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challengecreation',
            name='defendant_1',
        ),
        migrations.RemoveField(
            model_name='challengecreation',
            name='defendant_2',
        ),
        migrations.AddField(
            model_name='challengecreation',
            name='challenge',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Challenge'),
            preserve_default=False,
        ),
    ]
