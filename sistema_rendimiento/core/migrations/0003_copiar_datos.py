from django.conf import settings
from django.db import migrations, models


def copiar_propietarios(apps, schema_editor):
    """Cada core.Usuario pasa al User de Django con el mismo username; si no hay, al primer superusuario."""
    Usuario = apps.get_model('core', 'Usuario')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Categoria = apps.get_model('core', 'Categoria')
    Objetivo = apps.get_model('core', 'Objetivo')

    respaldo = User.objects.filter(is_superuser=True).order_by('pk').first() or User.objects.order_by('pk').first()
    for usuario in Usuario.objects.all():
        destino = User.objects.filter(username=usuario.username).first() or respaldo
        if destino is None:
            raise RuntimeError('No hay usuarios de Django a quién pasar los datos; crea uno con createsuperuser.')
        Categoria.objects.filter(usuario_id=usuario.pk).update(propietario=destino)
        Objetivo.objects.filter(usuario_id=usuario.pk).update(propietario=destino)


def cancelado_a_vencido(apps, schema_editor):
    apps.get_model('core', 'Objetivo').objects.filter(estado='cancelado').update(estado='vencido')


class Migration(migrations.Migration):
    """RF2, paso 2: copia los dueños. RF7: el estado "cancelado" pasa a "vencido"."""

    dependencies = [
        ('core', '0002_propietario_user'),
    ]

    operations = [
        migrations.RunPython(copiar_propietarios),
        migrations.RunPython(cancelado_a_vencido),
        migrations.AlterField(
            model_name='objetivo',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En progreso'), ('completado', 'Completado'), ('vencido', 'Vencido')], default='pendiente', max_length=20),
        ),
    ]
