# Generated by Django 5.0.4 on 2024-05-28 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0059_charge_last_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='correlation_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name=''),
        ),
    ]
