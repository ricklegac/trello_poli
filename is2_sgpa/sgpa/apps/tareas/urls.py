from django.urls import path, include
from tareas.views import (
    ListarUserStory,
    crearUserStory,
    eliminarUserStory,
    modificarUserStory,
)

urlpatterns = [
    path("nuevo/", crearUserStory, name="crear_tarea"),
    path("listar/", ListarUserStory.as_view(), name="listar_tareas"),
    path("eliminar/<int:id_tarea>/", eliminarUserStory, name="eliminar_tarea"),
    path("editar/<int:id_tarea>/", modificarUserStory, name="modificar_tarea"),
]
