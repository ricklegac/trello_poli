from django.urls import path
from .views import (
    CrearPerfil,
    ListarPerfil,
    administrador,
    concederAcceso,
    editarPerfil_Admin,
    editarPerfil_General,
    eliminarPerfil,
    home,
    listaAcceso,
    proyectosUsuario,
)


urlpatterns = [
    path("", home, name="home"),
    path("nuevo/", CrearPerfil.as_view(), name="solicitar_acceso"),
    path("listar/", ListarPerfil.as_view(), name="listar_perfiles"),
    path("<int:id_usuario>/", proyectosUsuario, name="proyectos_usuario"),
    path("perfil/<int:id_perfil>/", editarPerfil_General, name="editar_perfilGeneral"),
    path("administrador/", administrador, name="administrador"),
    path("acceso/", listaAcceso, name="lista_acceso"),
    path("editar/<int:id_perfil>/", editarPerfil_Admin, name="editar_perfil"),
    path("eliminar/<int:id_perfil>/", eliminarPerfil, name="eliminar_perfil"),
    path("administrador/<int:id_perfil>", concederAcceso, name="conceder_acceso"),
]
