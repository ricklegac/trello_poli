# Generated by Django 4.1.1 on 2022-12-15 21:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
        ("proyectos", "0012_columnas_orden"),
    ]

    operations = [
        migrations.AlterField(
            model_name="miembro",
            name="idPerfil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="miembros",
                to="usuarios.perfil",
            ),
        ),
    ]
