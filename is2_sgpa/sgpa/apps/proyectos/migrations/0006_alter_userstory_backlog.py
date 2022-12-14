# Generated by Django 4.1.1 on 2022-11-01 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("proyectos", "0005_alter_userstory_sprint"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userstory",
            name="backlog",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_stories",
                to="proyectos.backlog",
            ),
        ),
    ]
