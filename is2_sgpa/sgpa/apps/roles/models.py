from django.db import models
from django.contrib.auth.models import Group

# Create your models here.


class Rol(models.Model):
    grupo = models.OneToOneField(Group, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    proyecto = models.ForeignKey(
        to="proyectos.Proyecto", on_delete=models.CASCADE, null=True, blank=True
    )
    sprint = models.ManyToManyField(to="proyectos.Sprint", blank=True)

    class Meta:
        unique_together = ["nombre", "proyecto"]
        permissions = (
            ("Crear proyecto", "Permite crear proyectos"),
            ("Modificar proyecto", "Permite modificar proyectos"),
            ("Eliminar proyecto", "Permite eliminar proyectos"),
            ("Crear Sprint", "Permite crear un sprint"),
            ("Modificar Sprint", "Permite modificar un sprint"),
            ("Cancelar Sprint", "Permite cancelar un sprint"),
            ("Crear user story", "Permite crear un user story"),
            ("Modificar user story", "Permite modificar un user story"),
            ("Eliminar user story", "Permite eliminar un user story"),
        )
