# Generated by Django 5.0.4 on 2024-05-26 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0058_charge_attempts_alter_charge_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='last_error',
            field=models.TextField(blank=True, null=True),
        ),
    ]
