# Generated by Django 5.0.4 on 2024-05-30 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0030_charge_loja_ever_saldo_loja_is_active_loja_saldo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loja',
            name='capa',
            field=models.ImageField(blank=True, default='/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg', null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='loja',
            name='foto',
            field=models.ImageField(blank=True, default='/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg', null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='loja',
            name='tempo_entrega_max',
            field=models.IntegerField(blank=True, default=75, null=True),
        ),
        migrations.AlterField(
            model_name='loja',
            name='tempo_entrega_min',
            field=models.IntegerField(blank=True, default=65, null=True),
        ),
    ]
