from django.urls import path
from proyectos.views import (
    CrearRol,
    ListarRol,
    ListarUserStory,
    asignarRol,
    asignarSprint,
    asignarTareasSprint,
    avanzarEstadoTarea,
    cancelarSprint,
    crearTipoUS,
    crearUserStory,
    desasignarRol,
    desasignarSprint,
    editarRol,
    eliminarRol,
    eliminarUserStory,
    finalizarProyecto,
    finalizarSprint,
    home,
    iniciarSprint,
    miembroCrear,
    miembroEliminar,
    modificarUserStory,
    retrocederEstadoTarea,
    tableroKanban,
    verMiembros,
    verProyecto,
    crearProyecto,
    ListarTipoUserStory,
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
    eliminarTipo,
    verRoles,
    modificarTipoUS,
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
        "<int:id_proyecto>/sprint/modificar/<int:id_sprint>",
        modificarSprints,
        name="modificar_sprint",
    ),
    path("<int:id_proyecto>/sprint/listar", listarSprints, name="listar_sprints"),
    path(
        "<int:id_proyecto>/sprint/eliminar/<int:id_sprint>/",
        eliminarSprint,
        name="eliminar_sprint",
    ),
    path(
        "<int:id_proyecto>/sprint/iniciar/<int:id_sprint>/",
        iniciarSprint,
        name="iniciar_sprint",
    ),
    path(
        "<int:id_proyecto>/sprint/cancelar/<int:id_sprint>/",
        cancelarSprint,
        name="cancelar_sprint",
    ),
    path(
        "<int:id_proyecto>/sprint/finalizar/<int:id_sprint>/",
        finalizarSprint,
        name="finalizar_sprint",
    ),
    path(
        "<int:idProyecto>/sprint/kanban/<int:idSprint>/",
        tableroKanban,
        name="kanban",
    ),
    path(
        "<int:idProyecto>/sprint/tareas/<int:idSprint>/",
        asignarTareasSprint,
        name="sprint_tareas",
    ),
    path(
        "<int:idProyecto>/sprint/<int:idSprint>/tarea/<int:idTarea>/",
        asignarSprint,
        name="asignar_sprint",
    ),
    path(
        "<int:idProyecto>/sprint/<int:idSprint>/tarea/<int:idTarea>/desasignar_sprint",
        desasignarSprint,
        name="desasignar_sprint",
    ),
    path(
        "<int:idProyecto>/sprint/kanban/<int:idSprint>/tarea-avanzar/<int:idTarea>/",
        avanzarEstadoTarea,
        name="avanzar_tarea",
    ),
    path(
        "<int:idProyecto>/sprint/kanban/<int:idSprint>/tarea-retroceder/<int:idTarea>/",
        retrocederEstadoTarea,
        name="retroceder_tarea",
    ),
    # Historial
    path("<int:id_proyecto>/historial/", verHistorial, name="ver_historial"),
    # Miembros
    path("<int:idProyecto>/miembros/listar/", verMiembros, name="listar_miembros"),
    path("<int:idProyecto>/miembros/nuevo/", miembroCrear, name="nuevo_miembro"),
    path(
        "<int:idProyecto>/miembros/eliminar/<int:idMiembro>/",
        miembroEliminar,
        name="eliminar_miembro",
    ),
    path(
        "<int:idProyecto>/miembros/<int:idMiembro>/roles/", verRoles, name="ver_roles"
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
    path("<int:idProyecto>/roles/listar/", ListarRol.as_view(), name="listar_roles"),
    path(
        "<int:idProyecto>/roles/eliminar/<int:id_rol>/",
        eliminarRol,
        name="eliminar_rol",
    ),
    path("<int:idProyecto>/roles/editar/<int:id_rol>/", editarRol, name="editar_rol"),
    # User Stories
    path("<int:idProyecto>/tareas/nuevo/", crearUserStory, name="crear_tarea"),
    path(
        "<int:idProyecto>/tareas/listar/",
        ListarUserStory.as_view(),
        name="listar_tareas",
    ),
    path(
        "<int:idProyecto>/tipos/listar/",
        ListarTipoUserStory.as_view(),
        name="listar_tipos",
    ),
    path(
        "<int:idProyecto>/tipos/eliminar/<int:id_tipo>/",
        eliminarTipo,
        name="eliminar_tipo",
    ),
    path(
        "<int:idProyecto>/tipos/modificar/<int:id_tipo>/",
        modificarTipoUS,
        name="modificar_tipo",
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
    path(
        "<int:idProyecto>/tareas/tipo/",
        crearTipoUS,
        name="tipos_us",
    ),
]
