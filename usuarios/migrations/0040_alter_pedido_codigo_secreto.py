from django.db import migrations, models
import uuid

def generate_unique_codigo_secreto(apps, schema_editor):
    Pedido = apps.get_model('usuarios', 'Pedido')
    for pedido in Pedido.objects.all():
        pedido.codigo_secreto = uuid.uuid4()
        pedido.save()

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0039_pedido_codigo_secreto'),
    ]

    operations = [
        migrations.RunPython(generate_unique_codigo_secreto),
        migrations.AlterField(
            model_name='pedido',
            name='codigo_secreto',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]