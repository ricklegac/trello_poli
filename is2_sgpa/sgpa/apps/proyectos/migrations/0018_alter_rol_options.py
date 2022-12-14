# Generated by Django 4.1.1 on 2022-12-16 05:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("proyectos", "0017_alter_rol_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="rol",
            options={
                "permissions": (
                    ("iniciar_proyecto", "Permite iniciar proyectos"),
                    ("cancelar_proyecto", "Permite cancelar proyectos"),
                    ("crear_proyecto", "Permite crear proyectos"),
                    ("modificar_proyecto", "Permite modificar proyectos"),
                    ("eliminar_proyecto", "Permite eliminar proyectos"),
                    ("crear_sprint", "Permite crear un sprint"),
                    ("modificar_sprint", "Permite modificar un sprint"),
                    ("eliminar_sprint", "Permite eliminar un sprint"),
                    ("iniciar_sprint", "Permite iniciar un sprint"),
                    ("cancelar_sprint", "Permite cancelar un sprint"),
                    ("finalizar_sprint", "Permite finalizar un sprint"),
                    ("crear_user_story", "Permite crear un user story"),
                    ("modificar_user_story", "Permite modificar un user story"),
                    ("eliminar_user_story", "Permite eliminar un user story"),
                    ("crear_rol", "Permite crear un rol"),
                    ("modificar_rol", "Permite modificar un rol"),
                    ("eliminar_rol", "Permite eliminar un rol"),
                    ("asignar_desasignar_rol", "Permite asignar y desasignar un rol"),
                    ("agregar_miembros", "Permite agregar miembros"),
                    ("eliminar_miembros", "Permite eliminar miembros"),
                )
            },
        ),
    ]
