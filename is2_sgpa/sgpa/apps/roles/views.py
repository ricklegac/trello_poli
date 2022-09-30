from roles.models import Rol
from roles.forms import Rol_Form
from usuarios.models import Perfil
from miembros.models import Miembro
from django.urls.base import reverse
from proyectos.models import Proyecto, Historial
from django.shortcuts import redirect, render
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User


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
        return reverse("roles:listar_roles", args=(self.kwargs["idProyecto"],))

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

        return redirect("roles:listar_roles", idProyecto=idProyecto)
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

        return redirect("roles:listar_roles", idProyecto=idProyecto)
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
    return redirect("miembros:ver_roles", idProyecto=idProyecto, idMiembro=idMiembro)


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
    return redirect("miembros:ver_roles", idProyecto=idProyecto, idMiembro=idMiembro)


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
