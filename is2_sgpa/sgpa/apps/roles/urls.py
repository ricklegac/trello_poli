from django.urls import path, include
from roles.views import CrearRol, ListarRol, eliminarRol, editarRol

urlpatterns = [
    path("nuevo/", CrearRol.as_view(), name="crear_rol"),
    path("listar/", ListarRol.as_view(), name="listar_roles"),
    path("eliminar/<int:id_rol>/", eliminarRol, name="eliminar_rol"),
    path("editar/<int:id_rol>/", editarRol, name="editar_rol"),
]
