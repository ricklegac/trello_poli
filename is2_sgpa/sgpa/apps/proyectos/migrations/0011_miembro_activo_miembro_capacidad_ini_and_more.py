# Generated by Django 4.1.1 on 2022-12-15 15:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proyectos", "0010_userstory_horas_estimadas_userstory_horas_trabajadas"),
    ]

    operations = [
        migrations.AddField(
            model_name="miembro",
            name="activo",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="miembro",
            name="capacidad_ini",
            field=models.PositiveSmallIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(24),
                ],
            ),
        ),
        migrations.AddField(
            model_name="miembro",
            name="capacidad_pen",
            field=models.PositiveSmallIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(24),
                ],
            ),
        ),
        migrations.AddField(
            model_name="miembro",
            name="warning_cap",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sprint",
            name="equipo",
            field=models.ManyToManyField(related_name="+", to="proyectos.miembro"),
        ),
        migrations.AddField(
            model_name="sprint",
            name="warning_cap",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userstory",
            name="prioridad_funcional",
            field=models.PositiveSmallIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10),
                ],
            ),
        ),
        migrations.AddField(
            model_name="userstory",
            name="prioridad_tecnica",
            field=models.PositiveSmallIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10),
                ],
            ),
        ),
        migrations.AddField(
            model_name="userstory",
            name="prioridad_total",
            field=models.FloatField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(13),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="userstory",
            name="horas_estimadas",
            field=models.PositiveSmallIntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Horas estimadas",
            ),
        ),
    ]