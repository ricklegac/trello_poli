from django.contrib import admin
from proyectos.models import Miembro, Proyecto, Rol, Sprint, UserStory

# Register your models here.
admin.site.register(Proyecto)
admin.site.register(Sprint)
admin.site.register(Miembro)
admin.site.register(Rol)
admin.site.register(UserStory)
