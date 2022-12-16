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


class Miembro(models.Model):
    idPerfil = models.ForeignKey(
        to="usuarios.Perfil", on_delete=models.CASCADE, related_name="miembros"
    )
    idProyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    warning_cap = models.BooleanField(default=False)
    activo = models.BooleanField(
        default=False
    )  # Estado del Miembro, si esta Activo == True sino == False
    capacidad_pen = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
    )  # cantidad de horas por dia a trabajar
    capacidad_ini = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
    )


class Sprint(models.Model):
    objetivos = models.CharField(max_length=300, blank=False, null=True)
    posicion = models.IntegerField(blank=False, null=True)
    numTareas = models.IntegerField(default=0)
    duracion = models.FloatField(default=0)  # numero referido al numero de horas
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
    warning_cap = models.BooleanField(default=False)
    equipo = models.ManyToManyField(Miembro, related_name="+")

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
    orden = models.IntegerField(default=0)

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
    descripcion = models.TextField(null=True, blank=False, default="")
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
    horas_trabajadas = models.PositiveSmallIntegerField(
        verbose_name="Horas trabajadas", null=True, blank=True, default=0
    )
    horas_estimadas = models.PositiveSmallIntegerField(
        verbose_name="Horas estimadas",
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    prioridad_funcional = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    prioridad_tecnica = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    prioridad_total = models.FloatField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(13)],
    )

    def __str__(self):
        return self.nombre
