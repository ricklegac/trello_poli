# Generated by Django 4.1.1 on 2022-09-30 05:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ci', models.PositiveIntegerField(error_messages={'unique': 'CI no disponible'}, unique=True)),
                ('telefono', models.PositiveIntegerField(null=True)),
                ('roles', models.ManyToManyField(to='roles.rol')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
                'permissions': (('autorizar_usuario', 'Permite la administración del SGPA'), ('acceso_usuario', 'Permite el acceso a SGPA'), ('editar_usuario', 'Permite editar usuario'), ('eliminar_usuario', 'Permite eliminar usuario')),
            },
        ),
    ]
