from django.utils import tree
import proyectos.models
from django.db import models
from usuarios.models import Perfil
from django.db.models.deletion import CASCADE
from django.core.validators import MinValueValidator, MaxValueValidator

ESTADOUS_CHOICES = [
    ("En_Cola", "En Cola"),
    ("To_Do", "To Do"),
    ("Doing", "Doing"),
    ("Done", "Done"),
]


class UserStory(models.Model):

    backlog = models.ForeignKey(
        to="proyectos.Backlog",
        on_delete=models.CASCADE,
        null=True,
        related_name="user_stories",
    )
    nombre = models.CharField(max_length=150, blank=False)
    descripcion = models.TextField(max_length=300, blank=False)
    estado = models.CharField(default="En_Cola", max_length=7)
    desarrollador = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, null=True, blank=True
    )
    fechaCreacion = models.DateField(auto_now_add=True)
    fechaInicio = models.DateField(null=True)
    fechaFin = models.DateField(null=True)
    sprint = models.ForeignKey(
        to="proyectos.Sprint", on_delete=models.CASCADE, null=True
    )
    identificador = models.CharField(max_length=80, null=True)
    prioridad = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )

    class Meta:
        unique_together = ["identificador", "sprint"]

    def __str__(self):
        return "{}".format(self.identificador)
