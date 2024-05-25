# Generated by Django 5.0.4 on 2024-05-20 20:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0048_loja_stripe_payout_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompraAcumulada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_comprada', models.PositiveIntegerField(default=0)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.cliente')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.produto')),
            ],
        ),
        migrations.CreateModel(
            name='Promocao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_necessaria', models.PositiveIntegerField()),
                ('ativo', models.BooleanField(default=True)),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.loja')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.produto')),
            ],
        ),
    ]