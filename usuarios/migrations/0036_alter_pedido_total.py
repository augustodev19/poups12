# Generated by Django 5.0 on 2024-04-12 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0035_rename_preco_pedido_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
