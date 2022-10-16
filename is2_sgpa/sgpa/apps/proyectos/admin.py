from django.contrib import admin
from proyectos.models import Miembro, Proyecto, Rol, Sprint, TipoUserStory, UserStory

# Register your models here.
admin.site.register([Proyecto, Sprint, Miembro, Rol, UserStory, TipoUserStory])
