from django.urls import path
from roles.views import verRoles, asignarRol, desasignarRol
from miembros.views import miembroCrear, miembroEliminar, verMiembros


urlpatterns = [
    path("listar/", verMiembros, name="listar"),
    path("nuevo/", miembroCrear, name="nuevo"),
    path("<int:idMiembro>/eliminar/", miembroEliminar, name="eliminar"),
    path("<int:idMiembro>/roles/", verRoles, name="ver_roles"),
    path("<int:idMiembro>/roles/<int:idRol>/asignar/", asignarRol, name="asignar_rol"),
    path(
        "<int:idMiembro>/roles/<int:idRol>/desasignar/",
        desasignarRol,
        name="desasignar_rol",
    ),
]
