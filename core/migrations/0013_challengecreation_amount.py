# Generated by Django 2.2.1 on 2019-07-18 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20190716_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='challengecreation',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=22, max_digits=20),
            preserve_default=False,
        ),
    ]
