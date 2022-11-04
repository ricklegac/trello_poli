from django.db import models
from django.contrib.auth.models import Group
from django.utils import timezone

from django.core.validators import MinValueValidator, MaxValueValidator

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
    scrumMaster = models.ForeignKey(to="usuarios.Perfil", on_delete=models.CASCADE)
    equipo = models.OneToOneField(Group, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre


class Backlog(models.Model):
    nombre = models.CharField(max_length=20)
    posicion = models.IntegerField(blank=False, null=True)
    tipo = models.CharField(max_length=16, choices=TIPOBL_CHOICES)
    estado = models.CharField(max_length=8, choices=ESTADOBL_CHOICES, default="Vacio")
    fechaCreacion = models.DateField(auto_now_add=True)
    numTareas = models.IntegerField(default=0)
    proyecto = models.ForeignKey(
        Proyecto, null=True, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.nombre


class Sprint(models.Model):
    objetivos = models.CharField(max_length=300, blank=False, null=True)
    posicion = models.IntegerField(blank=False, null=True)
    numTareas = models.IntegerField(default=0)
    duracion = models.FloatField(default=0)  # numero referido al numero de semanas
    tiempo_disponible = models.FloatField(default=0)
    estado = models.CharField(
        max_length=10, choices=ESTADOSPR_CHOICES, default="En_cola"
    )
    proyecto = models.ForeignKey(
        Proyecto, null=True, blank=False, on_delete=models.CASCADE
    )
    fechaCreacion = models.DateField(auto_now_add=True)
    fechaInicio = models.DateField(null=True)
    fechaFin = models.DateField(null=True)

    def __str__(self):
        return self.objetivos


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


class Miembro(models.Model):
    idPerfil = models.ForeignKey(to="usuarios.Perfil", on_delete=models.CASCADE)
    idProyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)


class Rol(models.Model):
    grupo = models.OneToOneField(Group, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, null=True, blank=True
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

    def __str__(self):
        return self.nombre


class TipoUserStory(models.Model):
    nombre = models.CharField(max_length=150)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="proyectos"
    )

    def __str__(self):
        return self.nombre

    # class Meta:
    #     unique_together = ['nombre', 'proyecto']


class Columnas(models.Model):
    nombre = models.CharField(max_length=20)
    tipo_us = models.ForeignKey(
        TipoUserStory, on_delete=models.CASCADE, related_name="columnas"
    )
    opcional = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class UserStory(models.Model):

    backlog = models.ForeignKey(
        to="proyectos.Backlog",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_stories",
    )
    nombre = models.CharField(max_length=150, blank=False)
    descripcion = models.TextField(max_length=300, blank=False)
    estado = models.ForeignKey(
        to=Columnas, on_delete=models.CASCADE, null=True, blank=True
    )
    desarrollador = models.ForeignKey(
        to="usuarios.Perfil", on_delete=models.CASCADE, null=True, blank=True
    )
    fechaCreacion = models.DateField(auto_now_add=True)
    fechaInicio = models.DateField(default=timezone.now)
    fechaFin = models.DateField(null=True)
    sprint = models.ForeignKey(
        to="proyectos.Sprint", on_delete=models.CASCADE, null=True, blank=True
    )
    prioridad = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    tipo = models.ForeignKey(
        TipoUserStory, on_delete=models.CASCADE, related_name="user_stories"
    )

    def __str__(self):
        return self.nombre
