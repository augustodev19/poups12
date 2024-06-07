# Generated by Django 5.0.4 on 2024-06-05 15:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0042_loja_pontos'),
    ]

    operations = [
        migrations.CreateModel(
            name='LojaFuncionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aceitou_convite', models.BooleanField(default=False)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.cliente')),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.loja')),
            ],
        ),
        migrations.AddField(
            model_name='loja',
            name='funcionarios',
            field=models.ManyToManyField(related_name='empresas', through='usuarios.LojaFuncionario', to='usuarios.cliente'),
        ),
    ]