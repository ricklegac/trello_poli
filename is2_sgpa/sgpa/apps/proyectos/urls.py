from django.urls import path
from proyectos.views import (
    CrearRol,
    ListarRol,
    ListarUserStory,
    asignarRol,
    crearUserStory,
    desasignarRol,
    editarRol,
    eliminarRol,
    eliminarUserStory,
    finalizarProyecto,
    home,
    miembroCrear,
    miembroEliminar,
    modificarUserStory,
    verMiembros,
    verProyecto,
    crearProyecto,
    iniciarProyecto,
    cancelarProyecto,
    listarProyectos,
    eliminarProyecto,
    modificarProyecto,
    proy,
    crearSprint,
    listarSprints,
    verHistorial,
    modificarSprints,
    eliminarSprint,
    verRoles,
)

urlpatterns = [
    path("", proy, name="proy"),
    path("home/", home, name="home"),
    path("nuevo/", crearProyecto.as_view(), name="nuevo_proyecto"),
    path("listar/", listarProyectos.as_view(), name="listar_proyectos"),
    path("eliminar/<int:id_proyecto>/", eliminarProyecto, name="eliminar_proyectos"),
    path("<int:id_proyecto>/", verProyecto, name="ver_proyecto"),
    path("modificar/<int:id_proyecto>/", modificarProyecto, name="modificar_proyecto"),
    path("<int:id_proyecto>/iniciar/", iniciarProyecto, name="iniciar_proyecto"),
    path("<int:id_proyecto>/finalizar/", finalizarProyecto, name="finalizar_proyecto"),
    path("<int:id_proyecto>/cancelar/", cancelarProyecto, name="cancelar_proyecto"),
    path("<int:id_proyecto>/sprint", crearSprint, name="nuevo_sprint"),
    path(
        "<int:id_proyecto>/sprint/modificar", modificarSprints, name="modificar_sprint"
    ),
    path("<int:id_proyecto>/sprint/listar", listarSprints, name="listar_sprints"),
    path(
        "<int:id_proyecto>/sprint/eliminar/<int:id_sprint>/",
        eliminarSprint,
        name="eliminar_sprint",
    ),
    path("<int:id_proyecto>/historial/", verHistorial, name="ver_historial"),
]

urlpatterns += [
    # Miembros
    path("<int:idProyecto>/miembros/listar/", verMiembros, name="listar_miembros"),
    path("<int:idProyecto>/miembros/nuevo/", miembroCrear, name="nuevo_miembro"),
    path(
        "<int:idProyecto>/miembros/<int:idMiembro>/eliminar/",
        miembroEliminar,
        name="eliminar_miembro",
    ),
    path(
        "<int:idProyecto>/miembros/<int:idMiembro>/roles/",
        verRoles,
        name="ver_roles",
    ),
    path(
        "<int:idProyecto>/miembros/<int:idMiembro>/roles/<int:idRol>/asignar/",
        asignarRol,
        name="asignar_rol",
    ),
    path(
        "<int:idProyecto>/miembros/<int:idMiembro>/roles/<int:idRol>/desasignar/",
        desasignarRol,
        name="desasignar_rol",
    ),
    # Roles
    path("<int:idProyecto>/roles/nuevo/", CrearRol.as_view(), name="crear_rol"),
    path(
        "<int:idProyecto>/roles/listar/",
        ListarRol.as_view(),
        name="listar_roles",
    ),
    path(
        "<int:idProyecto>/roles/eliminar/<int:id_rol>/",
        eliminarRol,
        name="eliminar_rol",
    ),
    path(
        "<int:idProyecto>/roles/editar/<int:id_rol>/",
        editarRol,
        name="editar_rol",
    ),
    # User Stories
    path("<int:idProyecto>/tareas/nuevo/", crearUserStory, name="crear_tarea"),
    path(
        "<int:idProyecto>/tareas/listar/",
        ListarUserStory.as_view(),
        name="listar_tareas",
    ),
    path(
        "<int:idProyecto>/tareas/eliminar/<int:id_tarea>/",
        eliminarUserStory,
        name="eliminar_tarea",
    ),
    path(
        "<int:idProyecto>/tareas/editar/<int:id_tarea>/",
        modificarUserStory,
        name="modificar_tarea",
    ),
]
