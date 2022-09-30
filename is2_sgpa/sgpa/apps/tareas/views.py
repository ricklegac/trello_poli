from django.core.mail import send_mail
from django.http.response import HttpResponseRedirect
from usuarios.models import Perfil
from django.shortcuts import redirect, render
from tareas.models import UserStory
from django.urls.base import reverse
from tareas.forms import UserStoryEdit_Form, UserStoryForm
from django.contrib.auth.models import User
from proyectos.models import Backlog, Historial, Proyecto
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

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
#         return reverse("tareas:listar_tareas", args=(self.kwargs["idProyecto"],))

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
            return redirect("tareas:listar_tareas", idProyecto)
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

        return redirect("tareas:listar_tareas", idProyecto=idProyecto)
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

        return redirect("tareas:listar_tareas", idProyecto)
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
    return redirect("tareas:listar_tareas", idProyecto=idProyecto, idMiembro=idMiembro)
