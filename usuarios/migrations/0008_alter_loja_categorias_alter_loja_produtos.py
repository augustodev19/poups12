# Generated by Django 5.0 on 2023-12-19 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_remove_opcaocomplemento_complemento_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loja',
            name='categorias',
            field=models.ManyToManyField(blank=True, related_name='lojas', to='usuarios.categoria'),
        ),
        migrations.AlterField(
            model_name='loja',
            name='produtos',
            field=models.ManyToManyField(blank=True, to='usuarios.produto'),
        ),
    ]
