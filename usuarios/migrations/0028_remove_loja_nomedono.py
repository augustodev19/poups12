# Generated by Django 5.0 on 2024-03-21 04:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0027_loja_nomedono'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loja',
            name='nomeDono',
        ),
    ]
