from datetime import datetime
from django.forms import modelformset_factory
from django.forms.models import inlineformset_factory
from usuarios.models import Perfil
from django.contrib import messages
from django.contrib.auth.models import Group, Permission, User
from django.core.mail import send_mail
from django.urls.base import reverse_lazy
from django.views.generic import ListView
from proyectos.models import (
    Backlog,
    Columnas,
    Miembro,
    Proyecto,
    Rol,
    Sprint,
    Historial,
    TipoUserStory,
    UserStory,
)
from django.shortcuts import reverse, redirect, render
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin
from proyectos.forms import (
    AdicionalColumnaFormset,
    KanbanForm,
    MiembrosForm,
    Proyecto_Form,
    ProyectoEdit_Form,
    Rol_Form,
    Sprint_Form,
    SprintEdit_Form,
    TipoUserStoryForm,
    UserStoryEdit_Form,
    UserStoryForm,
)
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required


def base(request):
    return render(request, "base.html")


def proy(request):
    if request.user.is_authenticated:
        return render(request, "sprints/sprint.html")
    else:
        return redirect("login")


def home(request):
    return render(request, "home.html")


# --- Crear Proyecto --- #
class crearProyecto(LoginRequiredMixin, CreateView):
    """
    Vista basada en la clase CreateView para crear un nuevo proyecto
    No recibe parámetros
    Al completar los campos del formulario, guarda la información y redirige a la lista de los proyectos asociados
    Requiere inicio de sesión
    """

    model = Proyecto
    redirect_field_name = "redirect_to"
    form_class = Proyecto_Form
    template_name = "proyectos/nuevo_proyecto.html"

    def get_success_url(self):
        proyecto = Proyecto.objects.get(id=self.object.pk)
        scrummaster = Perfil.objects.get(id=self.request.POST.get("scrumMaster"))
        Miembro.objects.create(idPerfil=scrummaster, idProyecto=proyecto)
        equipo = Group.objects.create(name="equipo%s" % self.object.pk)
        proyecto.equipo = equipo
        proyecto.save()
        backlog = Backlog.objects.create(
            nombre="Product backlog", proyecto=proyecto, tipo="Product_Backlog"
        )
        backlog.save()

        tipo = TipoUserStory.objects.create(nombre="Estándar", proyecto=proyecto)
        tipo.save()

        columna = Columnas.objects.create(nombre="Cancelado", tipo_us=tipo, orden=-1)
        columna.save()
        columna = Columnas.objects.create(nombre="Inactivo", tipo_us=tipo, orden=0)
        columna.save()
        columna = Columnas.objects.create(nombre="To Do", tipo_us=tipo, orden=1)
        columna.save()
        columna = Columnas.objects.create(nombre="Doing", tipo_us=tipo, orden=2)
        columna.save()
        columna = Columnas.objects.create(nombre="Done", tipo_us=tipo, orden=3)
        columna.save()
        columna = Columnas.objects.create(nombre="Relese", tipo_us=tipo, orden=-2)
        columna.save()
        # El Done tiene que ser un backlog al que se pueda acceder para ver los US finalizados
        # columna = Columnas.objects.create(nombre="Done", tipo_us=tipo)
        # columna.save()

        # Done backlog
        backlog = Backlog.objects.create(
            nombre="Done", proyecto=proyecto, tipo="Sprint_Backlog"
        )
        backlog.save()

        user = User.objects.get(username=self.request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Crear Proyecto",
            autor=perfil.__str__(),
            proyecto=proyecto,
            categoria="Proyecto",
        )
        return reverse_lazy("usuarios:administrador")


# --- Listar Proyectos --- #
class listarProyectos(LoginRequiredMixin, ListView):
    """
    Vista basada en la clase ListView para listar los proyectos
    No recibe parámetros
    Muestra la lista de los proyectos asociados en forma de tabla
    Requiere inicio de sesión
    """

    model = Proyecto
    redirect_field_name = "redirect_to"
    template_name = "proyectos/listar_proyectos.html"
    ordering = ["id"]


# --- Eliminar Proyecto --- #
@login_required
def eliminarProyecto(request, id_proyecto):
    """
    Elimina el proyecto solicitado
    Recibe el request HTTP y el id del proyecto
    Retorna la renderización en el template especificado, en el cual solicita confirmación y luego redirige a la lista de proyectos
    Requiere inicio de sesión y permiso de administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    if proyecto.numSprints == 0:
        if request.method == "POST":
            proyecto.delete()
            return redirect("proyectos:listar_proyectos")
        return render(
            request,
            "proyectos/eliminar_proyecto.html",
            {"proyecto": proyecto},
        )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "No se puede eliminar el proyecto: existen %s sprints activos"
            % proyecto.numSprints,
        )
        return redirect("proyectos:listar_proyectos")


# --- Ver Proyecto --- #
@login_required
def verProyecto(request, id_proyecto):
    """
    Muestra el proyecto, la lista de los usuarios asociados y las funciones correspondientes al mismo
    Vista basada en función, para mostrar el menú de un proyecto
    Recibe el request HTTP y el id del poryecto correspondiente como parámetros
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprints = Sprint.objects.filter(proyecto=id_proyecto)
    miembros = Miembro.objects.filter(idProyecto=id_proyecto)

    return render(
        request,
        "proyectos/ver_proyecto.html",
        {"miembros": miembros, "proyecto": proyecto, "sprints": sprints},
    )


# --- Modificar Proyecto --- #
@login_required
def modificarProyecto(request, id_proyecto):
    """
    Vista basada en función, para actualizar un proyecto existente
    Recibe el request HTTP y el id del poryecto correspondiente como parámetros
    Al finalizar los cambios en los campos del formulario, guarda la información y redirige a la lista de los proyectos asociados
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)

    if request.method == "GET":
        proyecto_Form = ProyectoEdit_Form(instance=proyecto)
    else:
        proyecto_Form = ProyectoEdit_Form(request.POST, instance=proyecto)
        if proyecto_Form.is_valid():
            proyecto_Form.save()
            miembros = Miembro.objects.filter(idProyecto=proyecto)
            correos = []
            for miembro in miembros:
                correos.append(miembro.idPerfil.user.email)
            send_mail(
                "El proyecto ha sido modificado",
                "Usted es miembro del proyecto '{0}' y el mismo acaba de ser modificado, ingrese a la plataforma para observar los cambios.".format(
                    proyecto.nombre
                ),
                "is2.sgpa@gmail.com",
                correos,
            )
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Modificar Proyecto",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="Proyecto",
            )

        return redirect("proyectos:ver_proyecto", id_proyecto)
    return render(
        request,
        "proyectos/modificar_proyecto.html",
        {"proyecto_Form": proyecto_Form, "id_proyecto": id_proyecto},
    )


# --- Iniciar Proyecto --- #
@login_required
def iniciarProyecto(request, id_proyecto):
    """
    Función para cambiar el estado de un proyecto de 'Pendiente' a 'Iniciado'
    Recibe el request HTTP y el id del proyecto
    Previo al cambio de estado hace las comprobaciones correspondientes
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprints = Sprint.objects.filter(proyecto=id_proyecto).order_by("posicion")
    if proyecto.numSprints == 0:
        messages.error(request, "El sprint planning aún no fue realizado")
    else:

        if not sprints.filter(estado="Activo").exists():
            bandera = 0
            for sprint in sprints:
                if sprint.estado == "En_cola" and sprint.numTareas > 0:
                    sprint.estado = "Activo"
                    sprint.save()
                    bandera = 1
                    break
            if bandera == 0:
                messages.error(
                    request, "No existen tareas asignadas a ningún sprint disponible"
                )

        if sprints.filter(estado="Activo").exists():
            proyecto.estado = "Iniciado"
            proyecto.fechaInicio = datetime.now()
            proyecto.save()
            correos = []
            miembros = Miembro.objects.filter(idProyecto=proyecto)
            for miembro in miembros:
                correos.append(miembro.idPerfil.user.email)
            send_mail(
                "El proyecto ha sido iniciado",
                "Usted es miembro del proyecto '{0}' y el cuial acaba de ser iniciado, puede ingresar a la plataforma para realizar sus tareas.".format(
                    proyecto.nombre
                ),
                "is2.sgpa@gmail.com",
                correos,
            )
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Iniciar Proyecto",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="Proyecto",
            )
    return redirect("proyectos:ver_proyecto", id_proyecto)


# --- Cancelar Proyecto --- #
@login_required
def cancelarProyecto(request, id_proyecto):
    """
    Función que cambia el estado de un proyecto a 'Cancelado'
    Recibe el request HTTP y el id del proyecto que se desea cambiar
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprints = Sprint.objects.filter(proyecto=id_proyecto)
    for sprint in sprints:
        sprint.estado = "Cancelado"
        sprint.save()
    proyecto.estado = "Cancelado"
    proyecto.fechaFin = datetime.now()
    proyecto.save()
    miembros = Miembro.objects.filter(idProyecto=proyecto)
    correos = []
    for miembro in miembros:
        correos.append(miembro.idPerfil.user.email)
    send_mail(
        "El proyecto ha sido cancelado",
        "Usted es miembro del proyecto '{0}' y este acaba de ser cancelado.".format(
            proyecto.nombre
        ),
        "is2.sgpa@gmail.com",
        correos,
    )
    user = User.objects.get(username=request.user)
    perfil = Perfil.objects.get(user=user)
    Historial.objects.create(
        operacion="Cancelar Proyecto",
        autor=perfil.__str__(),
        proyecto=proyecto,
        categoria="Proyecto",
    )

    return redirect("proyectos:ver_proyecto", id_proyecto)


# --- Finalizar Proyecto --- #
@login_required()
def finalizarProyecto(request, id_proyecto):
    """
    Función que cambia el estado de un proyecto a 'Finalizado' si este cumple con las condiciones (todos los sprints finalizados)
    Recibe el request HTTP y el id del proyecto que se desea cambiar
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    # sprints = Sprint.objects.filter(proyecto=id_proyecto)
    # i = len(sprints)
    # for iterador in range(0, len(sprints)):
    #     if sprints[iterador].estado != "Finalizado":
    #         messages.add_message(request, messages.ERROR, "Sprint sin finalizar")
    #         i -= 1
    # if i == len(sprints):

    cancelado = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-1).first()
    release = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-2).first()

    if (
        UserStory.objects.filter(backlog__proyecto=proyecto)
        .exclude(estado=cancelado)
        .exclude(estado=release)
        .count()
        == 0
    ):
        product_backlog = Backlog.objects.filter(
            proyecto=proyecto, tipo="Product_Backlog"
        ).first()
        inactivo = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=0).first()
        tareas = UserStory.objects.filter(
            backlog__proyecto=proyecto, estado=release
        ).exclude()
        proyecto.estado = "Finalizado"
        proyecto.fechaFin = datetime.now()
        proyecto.save()

        for tarea in tareas:
            tarea.estado = inactivo
            tarea.backlog = product_backlog
            tarea.sprint = None
            tarea.save()

        miembros = Miembro.objects.filter(idProyecto=proyecto)
        correos = []
        for miembro in miembros:
            correos.append(miembro.idPerfil.user.email)
        send_mail(
            "Un proyecto ha sido finalizado",
            "Usted es miembro del proyecto '{0}' y este acaba de finalizar.".format(
                proyecto.nombre
            ),
            "is2.sgpa@gmail.com",
            correos,
        )
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Finalizar proyecto",
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=id_proyecto),
            categoria="Proyecto",
        )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "No se puede finalizar el proyecto, existen historias de usuario activas. Cambie sus estados a Cancelado o a Release",
        )
    return redirect("proyectos:ver_proyecto", id_proyecto)


# --- Ver Historial --- #
@login_required()
def verHistorial(request, id_proyecto):
    """
    Muestra el historial de cambios de todo el proyecto.
    Recibe el request HTTP y el id del proyecto.
    Muestra todos los mensajes guardados en el historial del proyecto desde que se creo.
    """
    historiales = Historial.objects.filter(proyecto=id_proyecto)
    proyecto = Proyecto.objects.get(id=id_proyecto)
    mensajes = []
    for x in range(0, len(historiales)):
        mensajes.append(historiales[x].__str__())
    return render(
        request,
        "proyectos/ver_historial.html",
        {"mensajes": mensajes, "idProyecto": id_proyecto, "proyecto": proyecto},
    )


# --- Crear Sprint --- #
@login_required
def crearSprint(request, id_proyecto):
    """
    Crea un sprint sobre el conjunto de User Stories seleccionados por el usuario
    Recibe el request HTTP y el id del proyecto
    Requiere inicio de sesión
    """
    proyecto = Proyecto.objects.get(id=id_proyecto)
    data = {"id_proyecto": id_proyecto}

    if request.method == "GET":
        data["form"] = Sprint_Form()
        return render(request, "sprints/nuevo_sprint.html", data)

    elif request.method == "POST":
        form = Sprint_Form(request.POST)
        if form.is_valid():
            proyecto.numSprints += 1
            proyecto.save()
            sprint = Sprint.objects.create(
                objetivos=form.cleaned_data["objetivos"],
                posicion=proyecto.numSprints,
                proyecto=proyecto,
                duracion=form.cleaned_data["duracion"],
                tiempo_disponible=form.cleaned_data["duracion"],
            )
            sprint.save()
            backlog = Backlog.objects.create(
                nombre=f"Sprint backlog {proyecto.numSprints}",
                proyecto=proyecto,
                tipo="Sprint_Backlog",
            )
            backlog.save()
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Crear User Story",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="User Story",
            )
            return redirect("proyectos:listar_sprints", id_proyecto)
        data["form"] = form
        return render(request, "sprints/nuevo_sprint.html", data)


# --- Modificar Sprints --- #
@login_required
def modificarSprints(request, id_proyecto, id_sprint):
    """
    Vista basada en funcion para modificar las Fases de un Proyecto existente.
    Recibe un 'request' y el 'id' del Proyecto correspondiente como parametros.
    Una vez completados los cambios en los campos del formulario, guarda la informacion
    actualizada y redirige a la lista de los proyectos asociados.
    """
    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprint = Sprint.objects.get(id=id_sprint)
    duracion_anterior = sprint.duracion
    if request.method == "GET":
        sprint_Form = SprintEdit_Form(instance=sprint)
    else:
        sprint_Form = SprintEdit_Form(request.POST, instance=sprint)
        if sprint_Form.is_valid():
            sprint_Form.save()
            duracion_nueva = sprint_Form.cleaned_data["duracion"]
            diferencia = duracion_nueva - duracion_anterior
            if sprint.tiempo_disponible + diferencia >= 0:
                sprint.tiempo_disponible += diferencia
                sprint.duracion = duracion_nueva
                sprint.save()
            else:
                messages.error(request, "La duración del sprint es insuficiente")
        else:
            print(sprint_Form.errors.items())

        return redirect("proyectos:listar_sprints", id_proyecto)

    return render(
        request,
        "sprints/modificar_sprint.html",
        {"sprint_Form": sprint_Form, "id_proyecto": id_proyecto},
    )


# --- Ver Sprints de un Proyecto --- #
@login_required
def listarSprints(request, id_proyecto):
    """
    Vista basada en función para mostrar los Sprints de un proyecto específico
    Recibe la petición http y el id del proyecto en cuestión
    Muestra la posición, el objetivo, el esado, número de tareas y las acciones posibles
    """
    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprint = Sprint.objects.filter(proyecto=proyecto).order_by("posicion")
    return render(
        request,
        "sprints/listar_sprints.html",
        {
            "sprints": sprint,
            "idProyecto": id_proyecto,
            "proyecto": proyecto,
        },
    )


# --- Eliminar Sprint --- #
@login_required
def eliminarSprint(request, id_proyecto, id_sprint):
    """
    Vista basada en funciones que permite eliminar un User Story seleccionado
    Recibe el request HTTP y el id del rol a eliminar
    Requiere inicio de sesión
    """
    sprint = Sprint.objects.get(id=id_sprint)

    if request.method == "POST":
        objetivo = sprint.objetivos
        sprint.delete()
        proyecto = Proyecto.objects.get(id=id_proyecto)
        proyecto.numSprints -= 1
        proyecto.save()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Eliminar Sprint con objetivo: {}".format(objetivo),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=id_proyecto),
            categoria="Sprint",
        )

        return redirect("proyectos:listar_sprints", id_proyecto)
    return render(
        request,
        "sprints/eliminar_sprint.html",
        {"sprint": sprint, "id_proyecto": id_proyecto},
    )


# --- Iniciar Sprint --- #
@login_required
def iniciarSprint(request, id_proyecto, id_sprint):
    """
    Función para cambiar el estado de un Sprint de 'En_cola' a 'Activo'
    Recibe el request HTTP y el id del sprint
    Previo al cambio de estado hace las comprobaciones correspondientes
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprint = Sprint.objects.get(id=id_sprint)

    if sprint.estado in ["Finalizado", "Cancelado"]:
        messages.error(request, "No se puede iniciar un sprint finalizado o cancelado")

    elif sprint.estado == "Activo":
        messages.error(request, "El sprint ya está activo")

    elif Sprint.objects.filter(proyecto=id_proyecto, estado="Activo").exists():
        messages.error(request, "Ya existe un sprint activo")
    else:
        if sprint.numTareas > 0:
            sprint.estado = "Activo"
            sprint.fechaInicio = datetime.now()
            sprint.save()

            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Iniciar Sprint",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="Sprint",
            )
        else:
            messages.error(request, "El sprint no contiene historias de usuario")
    return redirect("proyectos:listar_sprints", id_proyecto)


# --- Cancelar Sprint --- #
@login_required
def cancelarSprint(request, id_proyecto, id_sprint):
    """
    Función para cambiar el estado de un Sprint de 'En_cola' a 'Activo'
    Recibe el request HTTP y el id del sprint
    Previo al cambio de estado hace las comprobaciones correspondientes
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    sprint = Sprint.objects.get(id=id_sprint)

    if sprint.estado == "Finalizado":
        messages.error(request, "No se puede cancelar un sprint finalizado")

    elif sprint.estado == "Cancelado":
        messages.error(request, "El sprint ya fue cancelado")

    else:
        sprint.estado = "Cancelado"
        sprint.fechaFin = datetime.now()
        sprint.save()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Cancelar Sprint",
            autor=perfil.__str__(),
            proyecto=proyecto,
            categoria="Sprint",
        )
    return redirect("proyectos:listar_sprints", id_proyecto)


# --- Finalizar Sprint --- #
@login_required
def finalizarSprint(request, id_proyecto, id_sprint):
    """
    Función para cambiar el estado de un Sprint de 'En_cola' a 'Activo'
    Recibe el request HTTP y el id del sprint
    Previo al cambio de estado hace las comprobaciones correspondientes
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    product_backlog = Backlog.objects.filter(
        proyecto=proyecto, tipo="Product_Backlog"
    ).first()
    sprint = Sprint.objects.get(id=id_sprint)
    release = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-2).first()
    inactivo = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=0).first()
    tareas = UserStory.objects.filter(sprint=sprint).exclude(estado=release)

    if sprint.estado == "Cancelado":
        messages.error(request, "No se puede finalizar un sprint cancelado")

    elif sprint.estado == "Finalizado":
        messages.error(request, "El sprint ya fue finalizado")

    elif sprint.numTareas == 0:
        messages.error(request, "El sprint no contiene tareas")

    else:
        sprint.estado = "Finalizado"
        sprint.fechaFin = datetime.now()
        sprint.save()
        for tarea in tareas:
            tarea.estado = inactivo
            tarea.backlog = product_backlog
            tarea.sprint = None
            tarea.save()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Cancelar Sprint",
            autor=perfil.__str__(),
            proyecto=proyecto,
            categoria="Sprint",
        )
    return redirect("proyectos:listar_sprints", id_proyecto)


# --- Ver Sprint --- #
@login_required
def verSprint(request, id_proyecto, id_sprint):
    """
    Muestra el proyecto, la lista de los usuarios asociados y las funciones correspondientes al mismo
    Vista basada en función, para mostrar el menú de un proyecto
    Recibe el request HTTP y el id del poryecto correspondiente como parámetros
    """

    proyecto = Proyecto.objects.get(id=id_proyecto)
    backlog = Backlog.objects.get(proyecto=proyecto)
    tareas_PB = UserStory.objects.filter(backlog=backlog)
    sprint = Sprint.objects.get(id=id_sprint)
    tareas_SP = UserStory.objects.filter(sprint=id_sprint)

    return render(
        request,
        "proyectos/ver_proyecto.html",
        {"tareas_PB": tareas_PB, "proyecto": proyecto, "sprint": sprint},
    )


# ! Miembros
# --- Crear nuevo Miembro --- #
@login_required
def miembroCrear(request, idProyecto):
    """
    Vista basada en funciones que permite crear miembros
    Recibe el request HTTP y el id de un proyecto como parámetros
    Al finalizar la petición se retorna a la vista de lista de miembros
    Requiere inicio de sesión
    """

    if request.method == "POST":
        form = MiembrosForm(request.POST, idProyecto=idProyecto)

        if form.is_valid():
            miembro = form.save(commit=False)
            miembro.idProyecto = Proyecto.objects.get(id=idProyecto)
            miembro.save()
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Agregar a {} al proyecto".format(miembro.idPerfil.__str__()),
                autor=perfil.__str__(),
                proyecto=Proyecto.objects.get(id=idProyecto),
                categoria="Miembros",
            )

        return redirect("proyectos:listar_miembros", idProyecto=idProyecto)

    else:
        form = MiembrosForm(request.POST or None, idProyecto=idProyecto)

    return render(
        request, "miembros/nuevo_miembro.html", {"form": form, "idProyecto": idProyecto}
    )


# --- Eliminar Miembro --- #
@login_required
def miembroEliminar(request, idProyecto, idMiembro):
    """
    Vista basada en funciones que permite la eliminación de miembros
    Recibe el request HTTP, el id de un proyecto y el id de un miembro como parámeetros
    Una vez finalizada la petición se retorna a la lista de miembros
    Requiere inicio de sesión
    """

    miembro = Miembro.objects.get(idPerfil=idMiembro, idProyecto=idProyecto)
    if request.method == "POST":
        miembro.delete()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Eliminar a {} del proyecto".format(miembro.idPerfil.__str__()),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="Miembros",
        )
        return redirect("proyectos:listar_miembros", idProyecto=idProyecto)
    return render(
        request,
        "miembros/eliminar_miembro.html",
        {"miembros": miembro, "idProyecto": idProyecto},
    )


# --- Listar Miembros --- #
@login_required
def verMiembros(request, idProyecto):
    """
    Vista basada en funciones para listar miembros pertenecientes a un proyecto
    Recibe el request y el id de un proyecto como parámtros
    Requiere inicio de sesión
    """
    miembros = Miembro.objects.filter(idProyecto=idProyecto)
    proyecto = Proyecto.objects.get(id=idProyecto)

    return render(
        request,
        "miembros/ver_miembros.html",
        {
            "proyecto": proyecto,
            "miembros": miembros,
            "idProyecto": idProyecto,
        },
    )


# ! Apartado de Roles
# --- Vista para la creación de un rol --- #
class CrearRol(LoginRequiredMixin, CreateView):
    """
    Vista basada en modelos que permite crear un rol y el grupo asociado con los permisos correspondientes
    La Validación se redefine para permitir la creación del grupo y asociar los permisos correspondientes
    No recibe parámetros
    Requiere inicio de sesión
    """

    redirect_field_name = "redirect_to"
    model = Rol
    form_class = Rol_Form
    template_name = "roles/nuevo_rol.html"

    def get_success_url(self):
        return reverse("proyectos:listar_roles", args=(self.kwargs["idProyecto"],))

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(CrearRol, self).get_form_kwargs(**kwargs)
        form_kwargs["idProyecto"] = self.kwargs["idProyecto"]
        return form_kwargs

    def form_valid(self, form):
        proyecto = Proyecto.objects.get(id=self.kwargs["idProyecto"])
        form.instance.proyecto = proyecto
        nombreRol = form.cleaned_data["nombre"]
        nombreGrupo = "{}{}".format(nombreRol, proyecto.id)
        grupo = Group.objects.create(name=nombreGrupo)
        form.instance.grupo = grupo
        permisos = Permission.objects.filter(name__in=form.cleaned_data["select"])
        grupo.permissions.set(permisos)
        user = User.objects.get(username=self.request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Crear Rol {}".format(form.instance.nombre),
            autor=perfil.__str__(),
            proyecto=proyecto,
            categoria="Miembros",
        )

        return super(CrearRol, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CrearRol, self).get_context_data()
        context["idProyecto"] = self.kwargs["idProyecto"]
        context["proyecto"] = Proyecto.objects.get(id=self.kwargs["idProyecto"])
        return context


# --- Vista para listar roles existentes --- #
class ListarRol(LoginRequiredMixin, ListView):
    """
    Vista basada en modelos que permite listar todos los roles creados
    Muestra la lista de los roles asociados al proyecto en forma de tabla
    No recibe parámetros
    Requiere inicio de sesión
    """

    redirect_field_name = "redirect_to"
    model = Rol
    template_name = "roles/listar_roles.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ListarRol, self).get_context_data()
        context["idProyecto"] = self.kwargs["idProyecto"]
        proyecto = Proyecto.objects.get(id=context["idProyecto"])
        context["proyecto"] = proyecto
        return context

    def get_queryset(self):
        return Rol.objects.filter(proyecto=self.kwargs["idProyecto"]).order_by("id")


# --- Vista para eliminar un rol --- #
def eliminarRol(request, idProyecto, id_rol):
    """
    Vista basada en funciones que permite eliminar un rol seleccionado y su grupo asociado
    Recibe el request HTTP y el id del rol a eliminar
    Requiere inicio de sesión
    """

    rol = Rol.objects.get(id=id_rol)
    if request.method == "POST":
        grupo = Group.objects.get(id=rol.grupo.id)
        grupo.delete()
        nombre = rol.nombre
        rol.delete()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Eliminar Rol {}".format(nombre),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="Miembros",
        )

        return redirect("proyectos:listar_roles", idProyecto=idProyecto)
    return render(
        request, "roles/eliminar_rol.html", {"rol": rol, "idProyecto": idProyecto}
    )


# --- Vista para la edición de un rol --- #
@login_required
def editarRol(request, idProyecto, id_rol):
    """
    Vista basada en funciones que permite editar un rol seleccionado y su grupo asociado
    Recibe el request HTTP y el id del rol a editar
    Requiere inicio de sesión
    """

    rol = Rol.objects.get(id=id_rol)
    grupo = Group.objects.get(id=rol.grupo.id)
    if request.method == "GET":
        form = Rol_Form(instance=rol, idProyecto=idProyecto)
    else:
        form = Rol_Form(request.POST, instance=rol, idProyecto=idProyecto)
        if form.is_valid():
            permisos = Permission.objects.filter(name__in=form.cleaned_data["select"])
            grupo.permissions.set(permisos)
            form.save()
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Editar Rol {}".format(rol.nombre),
                autor=perfil.__str__(),
                proyecto=Proyecto.objects.get(id=idProyecto),
                categoria="Miembros",
            )

        return redirect("proyectos:listar_roles", idProyecto=idProyecto)
    return render(
        request, "roles/editar_rol.html", {"form": form, "idProyecto": idProyecto}
    )


# --- Asignación de un rol --- #
@login_required
def asignarRol(request, idProyecto, idMiembro, idRol):
    """
    Vista basada en funciones que permite asignar un rol seleccionado y su grupo asociado a un usuario miembro del proyecto
    Recibe el request HTTP, el id del proyecto asociado, el id miembro y el id del rol a asignar
    Requiere inicio de sesión
    """

    user = User.objects.get(id=idMiembro)
    rol = Rol.objects.get(id=idRol)
    rol.grupo.user_set.add(user)
    perfil = Perfil.objects.get(user=user)
    nombre = perfil.__str__()
    user = User.objects.get(username=request.user)
    perfil = Perfil.objects.get(user=user)
    Historial.objects.create(
        operacion="Asignar Rol {} a {}".format(rol.nombre, nombre),
        autor=perfil.__str__(),
        proyecto=Proyecto.objects.get(id=idProyecto),
        categoria="Miembros",
    )
    return redirect("proyectos:ver_roles", idProyecto=idProyecto, idMiembro=idMiembro)


# --- Revocar un rol --- #
@login_required
def desasignarRol(request, idProyecto, idMiembro, idRol):
    """
    Vista basada en funciones que permite revocar un rol seleccionado y su grupo asociado a un usuario miembro del proyecto
    Recibe el request HTTP, el id del proyecto asociado, el id del miembro y el id del rol a revocar
    Requiere inicio de sesión
    """

    user = User.objects.get(id=idMiembro)
    rol = Rol.objects.get(id=idRol)
    rol.grupo.user_set.remove(user)
    user = User.objects.get(username=request.user)
    perfil = Perfil.objects.get(user=user)
    Historial.objects.create(
        operacion="Desasignar Rol {} a {}".format(rol.nombre, perfil.__str__()),
        autor=perfil.__str__(),
        proyecto=Proyecto.objects.get(id=idProyecto),
        categoria="Miembros",
    )
    return redirect("proyectos:ver_roles", idProyecto=idProyecto, idMiembro=idMiembro)


# --- Ver todos los roles --- #
@login_required
def verRoles(request, idProyecto, idMiembro):
    """
    Vista basada en modelos que permite listar todos los reoles creados
    Recibe el request HTTP, el id del proyecto asociado y el id del miembro
    Requiere inicio de sesión
    """

    proyecto = Proyecto.objects.get(id=idProyecto)
    roles = Rol.objects.filter(proyecto=idProyecto)
    user = User.objects.get(id=idMiembro)
    roles_asignados = []
    roles_noasignados = []
    user = User.objects.get(id=idMiembro)
    for x in roles:
        roles_noasignados.append(x)

    for i in user.groups.filter(user=idMiembro):
        for x in roles:
            if i.name.startswith(x.nombre):
                roles_asignados.append(x)

    diferencia = set(roles_noasignados) - set(roles_asignados)
    roles_noasignados = list(diferencia)
    return render(
        request,
        "miembros/ver_roles.html",
        {
            "proyecto": proyecto,
            "roles_a": roles_asignados,
            "roles_sa": roles_noasignados,
            "idProyecto": idProyecto,
            "idMiembro": idMiembro,
        },
    )


# ! User Stories
# --- Crear User Story --- #
#     Vista basada en modelos que permite crear un User Story con los campos correspondientes
#     No recibe parámetros
#     Requiere inicio de sesión
#     """


# --- Listar User Story --- #
class ListarUserStory(LoginRequiredMixin, ListView):
    """
    Vista basada en modelos que permite listar todos los user stories creados
    Muestra la lista de los user stories asociados al proyecto en forma de tabla
    No recibe parámetros
    Requiere inicio de sesión
    """

    redirect_field_name = "redirect_to"
    model = UserStory
    template_name = "tareas/listar_userStory.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ListarUserStory, self).get_context_data()
        context["idProyecto"] = self.kwargs["idProyecto"]
        proyecto = Proyecto.objects.get(id=context["idProyecto"])
        context["proyecto"] = proyecto
        return context

    def get_queryset(self):
        proyecto = Proyecto.objects.get(id=self.kwargs["idProyecto"])
        backlog = Backlog.objects.get(proyecto=proyecto, tipo="Product_Backlog")
        return UserStory.objects.filter(backlog=backlog)


# --- Crear User Story --- #
@login_required
def crearUserStory(request, idProyecto):
    proyecto = Proyecto.objects.get(id=idProyecto)
    data = {"idProyecto": idProyecto}

    if request.method == "GET":
        data["form"] = UserStoryForm(idProyecto)
        return render(request, "tareas/nuevo_userStory.html", data)

    elif request.method == "POST":
        form = UserStoryForm(idProyecto, request.POST)
        if form.is_valid():
            backlog = Backlog.objects.get(proyecto=proyecto, tipo="Product_Backlog")
            # sprint = Sprint.objects.get(id=form.cleaned_data["sprint"].id)
            # sprint.numTareas += 1
            # sprint.save()
            backlog.numTareas += 1
            backlog.save()
            proyecto.save()
            tipo = form.cleaned_data["tipo"]
            estado = Columnas.objects.filter(tipo_us=tipo, orden=0).first()
            userStory = UserStory.objects.create(
                backlog=backlog,
                nombre=form.cleaned_data["nombre"],
                descripcion=form.cleaned_data["descripcion"],
                estado=estado,
                desarrollador=form.cleaned_data["desarrollador"],
                horas_estimadas=form.cleaned_data["horas_estimadas"],
                tipo=tipo,
                prioridad_funcional=form.cleaned_data["prioridad_funcional"],
                prioridad_tecnica=form.cleaned_data["prioridad_funcional"],
                prioridad_total=form.cleaned_data["prioridad_funcional"] * 0.6
                + form.cleaned_data["prioridad_funcional"] * 0.4,
            )
            userStory.save()
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Crear User Story",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="User Story",
            )
            return redirect("proyectos:listar_tareas", idProyecto)
        else:
            print(form.errors.items())
        data["form"] = form
        return render(request, "tareas/nuevo_userStory.html", data)


# --- Eliminar User Story --- #
@login_required
def eliminarUserStory(request, idProyecto, id_tarea):
    """
    Vista basada en funciones que permite eliminar un User Story seleccionado
    Recibe el request HTTP y el id del rol a eliminar
    Requiere inicio de sesión
    """

    userStory = UserStory.objects.get(id=id_tarea)

    if request.method == "POST":
        nombre = userStory.nombre
        userStory.delete()
        backlog = Backlog.objects.get(id=userStory.backlog.id)
        backlog.numTareas -= 1
        backlog.save()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Eliminar US {}".format(nombre),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="User Story",
        )

        return redirect("proyectos:listar_tareas", idProyecto=idProyecto)
    return render(
        request,
        "tareas/eliminar_tarea.html",
        {"userStory": userStory, "idProyecto": idProyecto},
    )


# --- Modificar User Story --- #
@login_required
def modificarUserStory(request, idProyecto, id_tarea):
    """
    Vista basada en función, para actualizar un User Story existente
    Recibe el request HTTP y el id del US correspondiente como parámetros
    Al finalizar los cambios en los campos del formulario, guarda la información y redirige a la lista de US asociados
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """
    proyecto = Proyecto.objects.get(id=idProyecto)
    tarea = UserStory.objects.get(id=id_tarea)
    backlog = tarea.backlog
    if request.method == "GET":
        tarea_Form = UserStoryEdit_Form(idProyecto, instance=tarea)
    else:
        tarea_Form = UserStoryEdit_Form(idProyecto, request.POST, instance=tarea)
        if tarea_Form.is_valid():
            tarea_Form.save()
            # desarrollador = tarea.desarrollador
            # send_mail(
            #     "El User Story ha sido modificado",
            #     "Usted es desarrollador del User Story '{0}' y este acaba de ser modificado, ingrese a la plataforma para observar los cambios".format(
            #         tarea.nombre
            #     ),
            #     "is2.sgpa@gmail.com",
            #     desarrollador,
            # )

            tarea.prioridad_total = (
                tarea_Form.cleaned_data["prioridad_funcional"] * 0.6
                + tarea_Form.cleaned_data["prioridad_tecnica"] * 0.4
            )
            tarea.save()

            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Modificar Proyecto",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="User Story",
            )

        return redirect("proyectos:listar_tareas", idProyecto)
    return render(
        request,
        "tareas/modificar_tarea.html",
        {
            "proyecto": proyecto,
            "tarea_Form": tarea_Form,
            "id_tarea": id_tarea,
            "idProyecto": idProyecto,
        },
    )


# --- Modificar User Story --- #
@login_required
def modificarUserStoryKanban(request, idProyecto, id_tarea):
    """
    Vista basada en función, para actualizar un User Story existente
    Recibe el request HTTP y el id del US correspondiente como parámetros
    Al finalizar los cambios en los campos del formulario, guarda la información y redirige a la lista de US asociados
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """
    proyecto = Proyecto.objects.get(id=idProyecto)
    tarea = UserStory.objects.get(id=id_tarea)
    idSprint = tarea.sprint.id
    if request.method == "GET":
        tarea_Form = UserStoryEdit_Form(idProyecto, instance=tarea)
    else:
        tarea_Form = UserStoryEdit_Form(idProyecto, request.POST, instance=tarea)
        if tarea_Form.is_valid():
            tarea_Form.save()
            # desarrollador = tarea.desarrollador
            # send_mail(
            #     "El User Story ha sido modificado",
            #     "Usted es desarrollador del User Story '{0}' y este acaba de ser modificado, ingrese a la plataforma para observar los cambios".format(
            #         tarea.nombre
            #     ),
            #     "is2.sgpa@gmail.com",
            #     desarrollador,
            # )
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Modificar Proyecto",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="User Story",
            )

        return redirect("proyectos:kanban", idProyecto, idSprint)
    return render(
        request,
        "tareas/modificar_tarea_kanban.html",
        {
            "proyecto": proyecto,
            "tarea_Form": tarea_Form,
            "id_tarea": id_tarea,
            "idProyecto": idProyecto,
            "idSprint": idSprint,
        },
    )


# --- Eliminar Tipo --- #
@login_required
def eliminarTipo(request, idProyecto, id_tipo):
    """
    Vista basada en funciones que permite eliminar un Tipo de User Story seleccionado
    Recibe el request HTTP y el id del rol a eliminar
    Requiere inicio de sesión
    """
    tipo = TipoUserStory.objects.get(id=id_tipo)
    columnas = Columnas.objects.filter(tipo_us=tipo)

    if request.method == "POST":
        nombre = tipo.nombre
        tipo.delete()
        for col in columnas:
            columnas.delete()
        proyecto = Proyecto.objects.get(id=idProyecto)
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Eliminar tipo de US: {}".format(nombre),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="Tipo de User Story",
        )

        return redirect("proyectos:listar_tipos", idProyecto)
    return render(
        request,
        "tareas/eliminar_tipo.html",
        {"tipo": tipo, "idProyecto": idProyecto},
    )


# --- Asignación de una tarea a un Sprint--- #
@login_required
def asignarSprint(request, idProyecto, idSprint, idTarea):

    tarea = UserStory.objects.get(id=idTarea)
    sprint = Sprint.objects.get(id=idSprint)
    sprint.numTareas += 1

    if (
        sprint.tiempo_disponible == 0
        or sprint.tiempo_disponible - tarea.horas_estimadas < 0
    ):
        sprint.warning_cap = True

    sprint.tiempo_disponible -= tarea.horas_estimadas
    sprint.save()

    columna = Columnas.objects.filter(
        tipo_us__proyecto=sprint.proyecto, orden=1
    ).first()
    tarea.sprint = sprint
    tarea.estado = columna
    tarea.save()

    user = User.objects.get(username=request.user)
    perfil = Perfil.objects.get(user=user)
    Historial.objects.create(
        operacion="Asignar User Story {} al sprint {}".format(
            tarea.nombre, sprint.objetivos
        ),
        autor=perfil.__str__(),
        proyecto=Proyecto.objects.get(id=idProyecto),
        categoria="Sprint",
    )
    return redirect("proyectos:sprint_tareas", idProyecto=idProyecto, idSprint=idSprint)


# --- Asignación de un User Story--- #
@login_required
def desasignarSprint(request, idProyecto, idSprint, idTarea):

    tarea = UserStory.objects.get(id=idTarea)
    sprint = Sprint.objects.get(id=idSprint)
    sprint.numTareas -= 1
    sprint.save()

    sprint.tiempo_disponible += tarea.horas_estimadas
    if sprint.tiempo_disponible > 0:
        sprint.warning_cap = False
    sprint.save()

    columna = Columnas.objects.filter(
        tipo_us__proyecto=sprint.proyecto, orden=0
    ).first()
    tarea.estado = columna
    tarea.sprint = None
    tarea.save()

    user = User.objects.get(username=request.user)
    perfil = Perfil.objects.get(user=user)
    Historial.objects.create(
        operacion="Se removió el User Story {} de nuevo al Product Backlog".format(
            tarea.nombre
        ),
        autor=perfil.__str__(),
        proyecto=Proyecto.objects.get(id=idProyecto),
        categoria="Product Backlog",
    )
    return redirect("proyectos:sprint_tareas", idProyecto=idProyecto, idSprint=idSprint)


# Agregar tipo de US
@login_required
def crearTipoUS(request, idProyecto):
    proyecto = Proyecto.objects.get(id=idProyecto)
    data = {"idProyecto": idProyecto}

    if request.method == "GET":
        data["form"] = TipoUserStoryForm()
        data["formset1"] = AdicionalColumnaFormset(
            queryset=Columnas.objects.none(), prefix="form1"
        )
        return render(request, "tareas/tipo.html", data)

    elif request.method == "POST":
        form = TipoUserStoryForm(request.POST)
        vacio1 = True
        formset1 = AdicionalColumnaFormset(request.POST, prefix="form1")
        i = 0
        for form1 in formset1:
            field = "form1-{}-nombre".format(i)
            nombre = form1.data[field]
            if nombre != "":
                vacio1 = False
            i += 1

        if form.is_valid() and formset1.is_valid() or vacio1:
            tipo_us = form.save(proyecto=proyecto)

            if not vacio1:
                for form1 in formset1:
                    adicional = form1.save(commit=False)
                    adicional.tipo_us = tipo_us
                    adicional.save()

            i = 1
            for columna in Columnas.objects.filter(tipo_us=tipo_us.id):
                columna.orden = i
                columna.save()
                i += 1

            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Crear Tipo de User Story",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="Tipo de User Story",
            )
            return redirect("proyectos:crear_tarea", idProyecto)
        data["form"] = form
        data["formset1"] = formset1
        return render(request, "tareas/tipo.html", data)


# ===Modificar Tipo de US===
def modificarTipoUS(request, idProyecto, id_tipo):
    """
    Modifica un tipo de US.
    Recibe la petición http, el id del proyecto y el id del tipo de US.
    Muestra la información del tipo de US especificado para su modificación y luego guarda
    los cambios realizados.
    """
    tipo = TipoUserStory.objects.get(id=id_tipo)
    columnas = Columnas.objects.filter(tipo_us=id_tipo)
    proyecto = Proyecto.objects.get(id=idProyecto)
    template_name = "tareas/tipo.html"
    if request.method == "GET":
        form = TipoUserStoryForm(instance=tipo, id=idProyecto)
        formset1 = AdicionalColumnaFormset(queryset=columnas, prefix="form1")
        return render(
            request,
            template_name,
            {
                "form": form,
                "formset1": formset1,
                "idProyecto": idProyecto,
            },
        )
    else:
        t = tipo
        t.nombre = "aux_cambio_is2_123"
        t.save()
        form = TipoUserStoryForm(request.POST, instance=tipo, id=idProyecto)
        vacio1 = True
        formset1 = AdicionalColumnaFormset(request.POST, prefix="form1")
        i = 0
        if not len(columnas) > 0:
            for form1 in formset1:
                field = "form1-{}-nombre".format(i)
                nombre = form1.data[field]
                if nombre != "":
                    vacio1 = False
                i += 1
            i = 0
        if form.is_valid() and (formset1.is_valid() or vacio1):
            tipo = form.save(proyecto=proyecto)
            if not vacio1 or (len(columnas) > 0):
                for form1 in formset1:
                    if form1.is_valid():
                        adicional = form1.save(commit=False)
                        adicional.tipo_us = tipo
                        adicional.save()
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Modificar Tipo de US {}".format(tipo.nombre),
                autor=perfil.__str__(),
                proyecto=Proyecto.objects.get(id=idProyecto),
                categoria="Tipo de User Story",
            )
        return redirect("proyectos:listar_tipos", idProyecto=idProyecto)


# --- Listar Tipo de User Story --- #
class ListarTipoUserStory(LoginRequiredMixin, ListView):
    """
    Vista basada en modelos que permite listar todos los user stories creados
    Muestra la lista de los user stories asociados al proyecto en forma de tabla
    No recibe parámetros
    Requiere inicio de sesión
    """

    redirect_field_name = "redirect_to"
    model = TipoUserStory
    template_name = "tareas/listar_tipos.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ListarTipoUserStory, self).get_context_data()
        context["idProyecto"] = self.kwargs["idProyecto"]
        proyecto = Proyecto.objects.get(id=context["idProyecto"])
        context["proyecto"] = proyecto
        return context

    def get_queryset(self):
        proyecto = Proyecto.objects.get(id=self.kwargs["idProyecto"])
        return TipoUserStory.objects.filter(proyecto=proyecto)


# --- Crear Tablero Kanban --- #
@login_required
def tableroKanban(request, idProyecto, idSprint):
    try:
        desarrollador = Perfil.objects.get(user=request.user)
    except:
        desarrollador = None

    proyecto = Proyecto.objects.get(id=idProyecto)
    cancelado = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-1).first()
    release = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-2).first()
    inactivo = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=0).first()
    sprint = Sprint.objects.get(id=idSprint)
    context = {"idProyecto": idProyecto}
    context["idSprint"] = idSprint
    context["sprint"] = sprint
    context["desarrollador"] = desarrollador
    context["scrumMaster"] = proyecto.scrumMaster
    context["proyecto"] = proyecto
    context["cancelado"] = cancelado
    context["release"] = release
    context["inactivo"] = inactivo

    if request.method == "GET":
        context["form"] = KanbanForm(idProyecto)
        tipos = TipoUserStory.objects.filter(proyecto=idProyecto).order_by("id")
        tipo = tipos.first()
        columnas = Columnas.objects.filter(tipo_us=tipo)
        datos = []
        for columna in columnas:
            datos.append(
                {
                    "columna": columna,
                    "idColumna": columna.id,
                    "tareas": UserStory.objects.filter(
                        estado=columna, sprint=sprint
                    ).order_by("-prioridad_total"),
                }
            )
        context["datos"] = datos
        return render(request, "sprints/tablero_kanban.html", context)

    elif request.method == "POST":
        form = KanbanForm(idProyecto, request.POST)
        tipo = TipoUserStory.objects.get(id=form.data["tipo"])

        columnas = []
        if tipo.nombre != "Estándar":
            admin_columnas = Columnas.objects.filter(
                orden__lte=0,
                tipo_us=TipoUserStory.objects.filter(proyecto=idProyecto).first(),
            )

            for columna in admin_columnas:
                columnas.append(columna)
            columnas.pop()

        columnas_x = Columnas.objects.filter(tipo_us=tipo)
        for columna in columnas_x:
            columnas.append(columna)

        if tipo.nombre != "Estándar":
            columnas.append(admin_columnas.last())

        datos = []
        for columna in columnas:
            datos.append(
                {
                    "columna": columna,
                    "idColumna": columna.id,
                    "tareas": UserStory.objects.filter(
                        estado=columna, sprint=sprint
                    ).order_by("-prioridad_total"),
                }
            )
        context["datos"] = datos
        context["form"] = form
        return render(request, "sprints/tablero_kanban.html", context)


# --- Cambiar el estado de un US --- #
@login_required
def avanzarEstadoTarea(request, idProyecto, idSprint, idTarea):

    tarea = UserStory.objects.get(id=idTarea)
    tipo = tarea.tipo
    columnas = Columnas.objects.filter(tipo_us=tipo)
    estado_temp = tarea.estado

    if tarea.estado == columnas.last():
        messages.error(
            request,
            "No se puede avanzar más",
        )
    else:
        for i in range(len(columnas)):
            if columnas[i] == tarea.estado:
                tarea.estado = columnas[i + 1]
                tarea.save()
                break

        columnas = columnas.order_by("orden")
        if tarea.estado == columnas.last():
            scrum_master = columnas.first().tipo_us.proyecto.scrumMaster
            correos = []
            correos.append(scrum_master)
            send_mail(
                "Un User Story en Release",
                "Usted es ScrumMaster y la tarea '{0}' acaba de llegar al estado finalizado, ingrese a la plataforma para observar los cambios y realizar seguimiento".format(
                    tarea.nombre
                ),
                "is2.sgpa@gmail.com",
                correos,
            )

        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="User Story cambió del estado {}  {}".format(
                estado_temp, tarea.estado
            ),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="Sprint",
        )
    return redirect("proyectos:kanban", idProyecto=idProyecto, idSprint=idSprint)


# --- Cambiar el estado de un US --- #
@login_required
def retrocederEstadoTarea(request, idProyecto, idSprint, idTarea):

    tarea = UserStory.objects.get(id=idTarea)
    tipo = tarea.tipo
    columnas = Columnas.objects.filter(tipo_us=tipo)
    estado_temp = tarea.estado

    if tarea.estado == columnas.first():
        messages.error(
            request,
            "No se puede retroceder más",
        )
    else:
        for i in range(len(columnas)):
            if columnas[i] == tarea.estado:
                tarea.estado = columnas[i - 1]
                tarea.save()
                break

        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="User Story cambió del estado {}  {}".format(
                estado_temp, tarea.estado
            ),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="Sprint",
        )
    return redirect("proyectos:kanban", idProyecto=idProyecto, idSprint=idSprint)


@login_required
def asignarTareasSprint(request, idProyecto, idSprint):
    proyecto = Proyecto.objects.get(id=idProyecto)
    context = {"idProyecto": idProyecto}
    context["proyecto"] = proyecto
    context["idSprint"] = idSprint
    context["cancelado"] = Columnas.objects.filter(
        tipo_us__proyecto=idProyecto, orden=-1
    ).first()
    if request.method == "GET":
        datos = []
        datos.append(
            {
                "columna": "Product Backlog",
                "tareas": UserStory.objects.filter(
                    backlog__proyecto=idProyecto, sprint=None
                ).order_by("-estado", "-prioridad_total"),
            }
        )
        datos.append(
            {
                "columna": "Sprint Backlog",
                "tareas": UserStory.objects.filter(
                    backlog__proyecto=idProyecto, sprint=idSprint
                ).order_by("-estado", "-prioridad_total"),
            }
        )
        context["datos"] = datos
        return render(request, "sprints/agregar_tareas.html", context)
    return redirect("proyectos:listar_tareas", idProyecto=idProyecto)


def cancelarUs(request, idProyecto):
    context = {"idProyecto": idProyecto}
    proyecto = Proyecto.objects.get(id=idProyecto)
    cancelado = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-1).first()
    release = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-2).first()

    if request.method == "POST":
        tareas = (
            UserStory.objects.filter(backlog__proyecto__id=idProyecto)
            .exclude(estado=cancelado)
            .exclude(estado=release)
        )
        for tarea in tareas:
            tarea.estado = cancelado
            tarea.save()
        cantidad = tareas.count()
        user = User.objects.get(username=request.user)
        perfil = Perfil.objects.get(user=user)
        Historial.objects.create(
            operacion="Se han cancelado {} historias de usuario".format(cantidad),
            autor=perfil.__str__(),
            proyecto=Proyecto.objects.get(id=idProyecto),
            categoria="User Story",
        )
        return redirect("proyectos:listar_tareas", idProyecto=idProyecto)
    return render(request, "tareas/cancelar_tareas.html", context)


class ListarUserStoryFinalizados(LoginRequiredMixin, ListView):
    """
    Vista basada en modelos que permite listar todos los user stories creados
    Muestra la lista de los user stories asociados al proyecto en forma de tabla
    No recibe parámetros
    Requiere inicio de sesión
    """

    redirect_field_name = "redirect_to"
    model = UserStory
    template_name = "tareas/tareas_finalizadas.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ListarUserStoryFinalizados, self).get_context_data()
        context["idProyecto"] = self.kwargs["idProyecto"]
        context["idSprint"] = self.kwargs["idSprint"]
        proyecto = Proyecto.objects.get(id=context["idProyecto"])
        context["proyecto"] = proyecto
        return context

    def get_queryset(self):
        print(self.kwargs)
        proyecto = Proyecto.objects.get(id=self.kwargs["idProyecto"])
        release = Columnas.objects.filter(tipo_us__proyecto=proyecto, orden=-2).first()
        tareas = UserStory.objects.filter(backlog__proyecto=proyecto, estado=release)
        return tareas


@login_required
def verUserStory(request, idProyecto, id_tarea):
    """
    Vista basada en función, para actualizar un User Story existente
    Recibe el request HTTP y el id del US correspondiente como parámetros
    Al finalizar los cambios en los campos del formulario, guarda la información y redirige a la lista de US asociados
    Requiere inicio de sesión y permisos de Scrum Master o administrador
    """
    proyecto = Proyecto.objects.get(id=idProyecto)
    tarea = UserStory.objects.get(id=id_tarea)
    if request.method == "GET":
        tarea_Form = UserStoryEdit_Form(idProyecto, instance=tarea)
    return render(
        request,
        "tareas/ver_tarea.html",
        {
            "proyecto": proyecto,
            "tarea": tarea,
            "id_tarea": id_tarea,
            "idProyecto": idProyecto,
        },
    )
