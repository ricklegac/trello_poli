from django.db import models
from usuarios.models import Perfil
from proyectos.models import Proyecto

# Create your models here.
class Miembro(models.Model):
    idPerfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    idProyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
