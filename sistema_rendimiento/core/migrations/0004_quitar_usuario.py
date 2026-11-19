import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """RF2, paso 3: el campo temporal se vuelve `usuario` y se borra el modelo core.Usuario."""

    dependencies = [
        ('core', '0003_copiar_datos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(model_name='categoria', name='usuario'),
        migrations.RemoveField(model_name='objetivo', name='usuario'),
        migrations.RenameField(model_name='categoria', old_name='propietario', new_name='usuario'),
        migrations.RenameField(model_name='objetivo', old_name='propietario', new_name='usuario'),
        migrations.AlterField(
            model_name='categoria',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='objetivo',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objetivos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(name='Usuario'),
    ]
