# Generated by Django 2.2.1 on 2019-07-10 21:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_challengecreation_challenge'),
    ]

    operations = [
        migrations.AddField(
            model_name='challengecreation',
            name='challenge',
            field=models.OneToOneField(default=99, on_delete=django.db.models.deletion.CASCADE, to='core.Challenge'),
            preserve_default=False,
        ),
    ]