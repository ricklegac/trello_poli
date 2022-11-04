from django.contrib import admin
from django.db import models
from django.forms import Textarea
from proyectos.models import (
    Backlog,
    Columnas,
    Miembro,
    Proyecto,
    Rol,
    Sprint,
    TipoUserStory,
    UserStory,
)

# Register your models here.
admin.site.register([Proyecto, Sprint, Miembro, Rol, UserStory, Backlog])


class ColumnasInline(admin.TabularInline):
    model = Columnas
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 100})},
    }
    min_num = 1
    extra = 0


@admin.register(TipoUserStory)
class TipoUserStoryAdmin(admin.ModelAdmin):
    inlines = (ColumnasInline,)
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 100})},
    }
    list_display = ("id", "nombre", "proyecto")
    list_display_links = ("id", "nombre")
    ordering = ("id", "nombre", "proyecto")
