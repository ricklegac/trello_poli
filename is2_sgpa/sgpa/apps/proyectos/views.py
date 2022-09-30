from datetime import datetime
from django.forms.models import inlineformset_factory
from usuarios.models import Perfil
from django.contrib import messages
from django.contrib.auth.models import Group, Permission, User
from django.core.mail import send_mail
from django.urls.base import reverse_lazy
from django.views.generic import ListView
from proyectos.models import (
    Backlog,
    Miembro,
    Proyecto,
    Rol,
    Sprint,
    Historial,
    UserStory,
)
from django.shortcuts import reverse, redirect, render, get_object_or_404
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin
from proyectos.forms import (
    MiembrosForm,
    Proyecto_Form,
    ProyectoEdit_Form,
    Rol_Form,
    Sprint_Form,
    UserStoryEdit_Form,
    UserStoryForm,
)
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required, permission_required


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
        Backlog.objects.create(proyecto=proyecto, tipo="Product_Backlog")
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
    sprints = Sprint.objects.filter(proyecto=id_proyecto)
    contador = 0
    if len(sprints) == proyecto.numSprints:
        contador += 1
        print("Existen Sprints xD")
    else:
        messages.add_message(
            request, messages.ERROR, "El sprint planning aún no fue realizado"
        )
        messages.error(request, "El sprint planning aún no fue realizado")

    if len(sprints) > 0:
        for tareas in range(0, len(sprints)):
            if len(UserStory.objects.filter(sprint=sprints[tareas])) > 0:
                contador += 1
                print("Encontró US")
            else:
                print("No se encontraron US")
                messages.add_message(
                    request,
                    messages.ERROR,
                    "No se encontraron Historias de Usuario para este sprint",
                )
    print("Contador es igual a = ", contador)
    contador += 1
    if contador == 2:
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
    sprints = Sprint.objects.filter(proyecto=id_proyecto)
    i = len(sprints)
    for iterador in range(0, len(sprints)):
        if sprints[iterador].estado != "Finalizado":
            messages.add_message(request, messages.ERROR, "Sprint sin finalizar")
            i -= 1
    if i == len(sprints):
        proyecto.estado = "Finalizado"
        proyecto.fechaFin = datetime.now()
        proyecto.save()
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
    return redirect("proyectos:ver_proyecto", id_proyecto)


# --- Crear Sprint --- #
# @login_required()
# def crearSprint(request, id_proyecto):
#     """
#     Crea un sprint sobre el conjunto de User Stories seleccionados por el usuario
#     Recibe el request HTTP y el id del proyecto
#     Actualiza la cantidad de Sprints y el estado de los User Stories
#     Requiere inicio de sesión
#     """

#     form = Sprint_Form(request.POST or None)
#     form.initial["proyecto"] = id_proyecto
#     proyecto = get_object_or_404(Proyecto, id=id_proyecto)
#     datos = {"proyecto": proyecto, "form": form, "title": "Crear Sprint"}
#     if form.is_valid():
#         if (
#             form.cleaned_data["fecha_inicio"] != None
#             and form.cleaned_data["fecha_fin"] != None
#         ):
#             ini = (form.cleaned_data["fecha_inicio"]).date()
#             fin = (form.cleaned_data["fecha_fin"]).date()
#             aux = (fin - ini).days
#             if aux >= 0:
#                 sprint = form.save()
#             else:
#                 datos["Error_fechas"] = True
#                 template = "sprints/nuevo_sprint.html"
#                 return render(request, template, datos)
#         else:
#             sprint = form.save()

#     if request.method == "POST":
#         return redirect(reverse("sprint", kwargs={"proyecto_id": proyecto.id}))
#     else:
#         template = "sprints/nuevo_sprint.html"
#         return render(request, template, datos)


# --- Ver Sprints --- #
# @login_required
# def listarSprints(request, id_proyecto):
#     """
#     Vista basada en funciones para listar los sprints
#     Muestra la lista de los sprints asociados en forma de tabla
#     Recibe el request HTTP y el id de un proyecto
#     Requiere inicio de sesión
#     """
#     sprints = Sprint.objects.filter(proyecto_id=id_proyecto)
#     print("OBJ SPRINT: ", sprints)

#     return render(
#         request,
#         "sprints/listar_sprints.html",
#         {
#             "sprints": sprints,
#             "id_proyecto": id_proyecto,
#         },
#     )


# --- Ver Historial --- #
@login_required()
def verHistorial(request, id_proyecto):
    """
    Muestra el historial de cambios de todo el proyecto.
    Recibe el request HTTP y el id del proyecto.
    Muestra todos los mensajes guardados en el historial del proyecto desde que se creo.
    """
    historiales = Historial.objects.filter(proyecto=id_proyecto)
    mensajes = []
    for x in range(0, len(historiales)):
        mensajes.append(historiales[x].__str__())
    return render(
        request,
        "proyectos/ver_historial.html",
        {"mensajes": mensajes, "idProyecto": id_proyecto},
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
        print("LLEGA")
        if form.is_valid():
            print("VALIDO")
            proyecto.numSprints += 1
            proyecto.save()
            Backlog.objects.create(
                posicion=proyecto.numSprints, proyecto=proyecto, tipo="Sprint_Backlog"
            )
            Backlog.objects.create(proyecto=proyecto, tipo="To_Do")
            Backlog.objects.create(proyecto=proyecto, tipo="Doing")
            Backlog.objects.create(proyecto=proyecto, tipo="Done")

            sprint = Sprint.objects.create(
                objetivos=form.cleaned_data["objetivos"],
                posicion=proyecto.numSprints,
                proyecto=proyecto,
                fechaInicio=form.cleaned_data["fechaInicio"],
                fechaFin=form.cleaned_data["fechaFin"],
            )
            sprint.save()
            user = User.objects.get(username=request.user)
            perfil = Perfil.objects.get(user=user)
            Historial.objects.create(
                operacion="Crear User Story",
                autor=perfil.__str__(),
                proyecto=proyecto,
                categoria="User Story",
            )
            return redirect("proyectos:listar_sprints", id_proyecto)
        print("NO VALIDO")
        data["form"] = form
        return render(request, "sprints/nuevo_sprint.html", data)


# --- Modificar Sprints --- #
@login_required
def modificarSprints(request, id_proyecto):
    """
    Vista basada en funcion para modificar las Fases de un Proyecto existente.
    Recibe un 'request' y el 'id' del Proyecto correspondiente como parametros.
    Una vez completados los cambios en los campos del formulario, guarda la informacion
    actualizada y redirige a la lista de los proyectos asociados.
    """
    proyecto = Proyecto.objects.get(id=id_proyecto)
    SprintFormSet = inlineformset_factory(
        Proyecto,
        Sprint,
        fields=(
            "objetivos",
            "posicion",
        ),
        can_delete=False,
        extra=proyecto.numSprints,
        max_num=proyecto.numSprints,
    )

    if request.method == "GET":
        formset = SprintFormSet(instance=proyecto)
    else:
        formset = SprintFormSet(request.POST, instance=proyecto)
        if formset.is_valid():
            # for x in range(0, len(formset)):
            #     if formset[x].cleaned_data.get("posicion") > proyecto.numSprints:
            #         messages.add_message(
            #             request,
            #             messages.ERROR,
            #             'Posición del sprint con objetivo "%s" no compatible'
            #             % formset[x].cleaned_data.get("objetivos"),
            #         )
            #         return redirect("proyectos:modificar_sprints", id_proyecto)
            #     for z in range(x + 1, len(formset)):
            #         if formset[x].cleaned_data.get("posicion") == formset[
            #             z
            #         ].cleaned_data.get("posicion"):
            #             messages.add_message(
            #                 request,
            #                 messages.ERROR,
            #                 "Las sprints '{0}' y '{1} tienen posiciones repetidas".format(
            #                     formset[x].cleaned_data.get("objetivos"),
            #                     formset[z].cleaned_data.get("objetivos"),
            #                 ),
            #             )
            #             return redirect("proyectos:modificar_sprints", id_proyecto)
            formset.save()

        return redirect("proyectos:ver_proyecto", id_proyecto)

    return render(
        request,
        "sprints/nuevo_sprint.html",
        {"formset": formset, "id_proyecto": id_proyecto},
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
    sprint = Sprint.objects.filter(proyecto=proyecto)
    return render(
        request,
        "sprints/listar_sprints.html",
        {"sprints": sprint, "proyecto": id_proyecto},
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

    return render(
        request,
        "miembros/ver_miembros.html",
        {
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

    roles = Rol.objects.filter(proyecto=idProyecto)
    user = User.objects.get(id=idMiembro)
    roles_asignados = []
    roles_noasignados = []
    user = User.objects.get(id=idMiembro)
    print(user.id)
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
            "roles_a": roles_asignados,
            "roles_sa": roles_noasignados,
            "idProyecto": idProyecto,
            "idMiembro": idMiembro,
        },
    )


# ! User Stories
# --- Crear User Story --- #
# class CrearUserStory(LoginRequiredMixin, CreateView):
#     """
#     Vista basada en modelos que permite crear un User Story con los campos correspondientes
#     No recibe parámetros
#     Requiere inicio de sesión
#     """

#     redirect_field_name = "redirect_to"
#     model = UserStory
#     form_class = UserStoryForm
#     template_name = "tareas/nuevo_userStory.html"

#     def get_success_url(self):
#         return reverse("proyectos:listar_tareas", args=(self.kwargs["idProyecto"],))

#     def get_form_kwargs(self, **kwargs):
#         form_kwargs = super(CrearUserStory, self).get_form_kwargs(**kwargs)
#         form_kwargs["idProyecto"] = self.kwargs["idProyecto"]
#         return form_kwargs

#     def form_valid(self, form):
#         proyecto = Proyecto.objects.get(id=self.kwargs["idProyecto"])
#         form.instance.proyecto = proyecto
#         backlog = Backlog.objects.get(proyecto=proyecto, tipo="Product_Backlog")
#         backlog.numTareas += 1
#         user = User.objects.get(username=self.request.user)
#         perfil = Perfil.objects.get(user=user)
#         Historial.objects.create(
#             operacion="Crear User Story {}".format(form.instance.nombre),
#             autor=perfil.__str__(),
#             proyecto=proyecto,
#             categoria="User Story",
#         )
#         return super(CrearUserStory, self).form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super(CrearUserStory, self).get_context_data(**kwargs)
#         context["idProyecto"] = self.kwargs["idProyecto"]
#         return context


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
        return context

    def get_queryset(self):
        proyecto = Proyecto.objects.get(id=self.kwargs["idProyecto"])
        backlog = Backlog.objects.get(proyecto=proyecto, tipo="Product_Backlog")
        print("IMPRESION", backlog)
        return UserStory.objects.filter(backlog=backlog)


# --- Crear User Story --- #
@login_required
def crearUserStory(request, idProyecto):
    proyecto = Proyecto.objects.get(id=idProyecto)
    data = {"idProyecto": idProyecto}

    if request.method == "GET":
        data["form"] = UserStoryForm()
        return render(request, "tareas/nuevo_userStory.html", data)

    elif request.method == "POST":
        form = UserStoryForm(request.POST)

        if form.is_valid():
            backlog = Backlog.objects.get(proyecto=proyecto, tipo="Product_Backlog")
            backlog.numTareas += 1
            backlog.save()
            proyecto.save()
            userStory = UserStory.objects.create(
                backlog=backlog,
                nombre=form.cleaned_data["nombre"],
                descripcion=form.cleaned_data["descripcion"],
                prioridad=form.cleaned_data["prioridad"],
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
        backlog = Backlog.objects.get(id=userStory.backlog)
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
    tarea = UserStory.objects.get(id=id_tarea)

    if request.method == "GET":
        tarea_Form = UserStoryEdit_Form(instance=tarea)
    else:
        tarea_Form = UserStoryEdit_Form(request.POST, instance=tarea)
        if tarea_Form.is_valid():
            tarea_Form.save()
            desarrollador = tarea.desarrollador
            send_mail(
                "El User Story ha sido modificado",
                "Usted es desarrollador del User Story '{0}' y este acaba de ser modificado, ingrese a la plataforma para observar los cambios".format(
                    tarea.nombre
                ),
                "is2.sgpa@gmail.com",
                desarrollador,
            )
            backlog = Backlog.objects.get(id=tarea.backlog)
            proyecto = Proyecto.objects.get(id=backlog.proyecto)

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
        {"tarea_Form": tarea_Form, "id_tarea": id_tarea, "idProyecto": idProyecto},
    )


# --- Asignación de un User Story--- #
@login_required
def asignarSprint(request, idProyecto, idMiembro, id_tarea):

    user = User.objects.get(id=idMiembro)
    perfil = Perfil.objects.get(user=user)
    userStory = UserStory.objects.get(id=id_tarea)
    userStory.desarrollador = perfil
    nombre = perfil.__str__()
    user = User.objects.get(username=request.user)
    perfil = Perfil.objects.get(user=user)
    Historial.objects.create(
        operacion="Asignar User Story {} a {}".format(userStory.nombre, nombre),
        autor=perfil.__str__(),
        proyecto=Proyecto.objects.get(id=idProyecto),
        categoria="User Story",
    )
    return redirect(
        "proyectos:listar_tareas", idProyecto=idProyecto, idMiembro=idMiembro
    )
