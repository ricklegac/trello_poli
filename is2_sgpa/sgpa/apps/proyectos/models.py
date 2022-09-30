from django.db import models
from tareas.models import UserStory
from usuarios.models import Perfil
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import Group, User

ESTADOPROY_CHOICES = [
    ("Pendiente", "Pendiente"),
    ("Iniciado", "Iniciado"),
    ("Cancelado", "Cancelado"),
    ("Finalizado", "Finalizado"),
]

ESTADOSPR_CHOICES = [
    ("En_cola", "En cola"),
    ("Activo", "Activo"),
    ("Cancelado", "Cancelado"),
    ("Finalizado", "Finalizado"),
]

ESTADOBL_CHOICES = [
    ("Vacio", "Vacio"),
    ("Cargado", "Cargado"),
]

TIPOBL_CHOICES = [
    ("Product_Backlog", "Product_Backlog"),
    ("Sprint_Backlog", "Sprint_Backlog"),
    ("Doing", "Doing"),
    ("To_Do", "To_Do"),
    ("Done", "Done"),
]


class Proyecto(models.Model):
    nombre = models.CharField(max_length=50, blank=False)
    descripcion = models.TextField(max_length=200, blank=False)
    fechaCreacion = models.DateField(auto_now_add=True)
    fechaInicio = models.DateField(null=True)
    fechaFin = models.DateField(null=True)
    estado = models.CharField(
        default="Pendiente",
        max_length=10,
        null=False,
        blank=False,
        choices=ESTADOPROY_CHOICES,
    )
    numSprints = models.IntegerField(default=0)
    scrumMaster = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    equipo = models.OneToOneField(Group, on_delete=models.CASCADE, null=True)

    def str(self):
        return "{}".format(self.nombre)


class Backlog(models.Model):
    posicion = models.IntegerField(blank=False, null=True)
    tipo = models.CharField(max_length=16, choices=TIPOBL_CHOICES)
    estado = models.CharField(max_length=8, choices=ESTADOBL_CHOICES, default="Vacio")
    fechaCreacion = models.DateField(auto_now_add=True)
    numTareas = models.IntegerField(default=0)
    proyecto = models.ForeignKey(
        Proyecto, null=True, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{}".format(self.estado)


class Sprint(models.Model):
    objetivos = models.CharField(max_length=300, blank=False, null=True)
    posicion = models.IntegerField(blank=False, null=True)
    numTareas = models.IntegerField(default=0)
    duracion = models.IntegerField(default=0)  # entero referido al numero de semanas
    estado = models.CharField(
        max_length=10, choices=ESTADOSPR_CHOICES, default="En_cola"
    )
    proyecto = models.ForeignKey(
        Proyecto, null=True, blank=False, on_delete=models.CASCADE
    )
    fechaCreacion = models.DateField(auto_now_add=True)
    fechaInicio = models.DateField(null=True)
    fechaFin = models.DateField(null=True)

    def str(self):
        return "{}".format(self.estado)


class Historial(models.Model):
    categoria = models.CharField(max_length=80)
    operacion = models.CharField(max_length=150)
    fecha = models.DateTimeField(auto_now_add=True)
    autor = models.CharField(max_length=80, null=True)
    proyecto = models.ForeignKey(
        Proyecto, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} {}: {}".format(
            self.fecha.strftime("%d/%m/%Y %X"), self.autor, self.operacion
        )
