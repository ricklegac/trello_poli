from django.db.models import Q
from usuarios.models import Perfil
from django.contrib import messages
from django.urls import reverse_lazy
from proyectos.models import Miembro, Proyecto
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from usuarios.forms import Perfil_Form, Usuario_Form, PerfilEdit_Form
from django.contrib.auth.models import User, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

#def home
def home(request):
    """
        :param root_path: root path to search isHiddenWithinTree, defaults to "../data_in/"
        :type root_path: str, optional
    """
    if request.user.is_authenticated:
        return render(request, "home.html")
    else:
        return redirect("login")


# --- Creación de Perfil --- #
#crear perfil
class CrearPerfil(LoginRequiredMixin, CreateView):
    """
    Clase para la creacion de un perfil de usuario
    Hereda de la clase genérica CreateView
    Requiere inicio de sesión
    """

    model = Perfil
    form_class = Perfil_Form
    template_name = "usuarios/nuevo_perfil.html"
    success_url = reverse_lazy("proyectos:home")

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user)
        Perfil.objects.create(
            user=user,
            ci=self.request.POST["ci"],
            telefono=self.request.POST["telefono"],
        )
        return redirect(self.success_url)


# --- Edición de Perfil --- #
#editar perfil general
@login_required
def editarPerfil_General(request, id_perfil):
    """
    Vista para la edición de los datos de un usuario (el email y el ci no puede ser modificado)
    Recibe el request HTTP y el id del perfil de un usuario
    Devuelve la renderización de la información del usuario
    Requiere inicio de sesión
    """
    perfil = Perfil.objects.get(id=id_perfil)
    usuario = User.objects.get(id=perfil.user.id)
    if request.method == "GET":
        perfil_Form = PerfilEdit_Form(instance=perfil)
        usuario_Form = Usuario_Form(instance=usuario)
    else:
        perfil_Form = PerfilEdit_Form(request.POST, instance=perfil)
        usuario_Form = Usuario_Form(request.POST, instance=usuario)
        if all([perfil_Form.is_valid(), usuario_Form.is_valid()]):
            perfil_Form.save(usuario=usuario, telefono=perfil.telefono)
            usuario_Form.save()
        return redirect("usuarios:proyectos_usuario", id_perfil)
    return render(
        request,
        "usuarios/editar_perfilGeneral.html",
        {"perfil_Form": perfil_Form, "usuario_Form": usuario_Form},
    )


# --- Proyectos de Usuario --- #
#proyecto de usuarios
@login_required
def proyectosUsuario(request, id_usuario):
    """
    Función que permite visualizar los proyectos de un determinado usuario
    Recibe el request HTTP y el id del usuario
    Retorna la renderización de los proyectos asociados en el template detallado
    Requiere inicio de sesión
    """

    usuario = User.objects.get(id=id_usuario)
    perfil = Perfil.objects.get(user=usuario)
    miembro = Miembro.objects.filter(idPerfil=perfil.id)
    return render(request, "usuarios/proyectos.html", {"miembros": miembro})


# ******************************** #
# *    Apartado Administrador    * #
# ******************************** #


@login_required
@permission_required("usuarios.autorizar_usuario", login_url="usuarios:home")
def administrador(request):
    """
    Obtiene la información acerca de todos los proyectos existentes, las solicitudes de acceso al sistema y el control de usuarios
    Recibe el request HTTP
    Retorna la renderización de la información ya mencionada en el template especificado
    Requiere inicio de sesión y permisos administrador
    """

    proyectos = Proyecto.objects.all()
    permiso = Permission.objects.get(codename="acceso_usuario")
    usuario = User.objects.filter(~Q(user_permissions=permiso), ~Q(id=1))
    perfilesAcceso = Perfil.objects.none()
    if len(usuario) > 0:
        perfilesAcceso = Perfil.objects.filter(Q(user=usuario[0]))
        for x in range(1, len(usuario)):
            perfilesAcceso |= Perfil.objects.filter(Q(user=usuario[x]))
    return render(
        request,
        "usuarios/administrador.html",
        {"perfilesAcceso": perfilesAcceso, "proyectos": proyectos},
    )


# --- Listar Solicitudes de Acceso --- #
#lista de accesos
@login_required
@permission_required("usuarios.autorizar_usuario", login_url="usuarios:home")
def listaAcceso(request):
    """
    Lista de las solicitudes de acceso al sistema
    Retorna la rendererización de la información solicitada en el template
    Recibe el request HTTP
    Requiere inicio de sesión y permisos administrador
    """

    perm = Permission.objects.get(codename="acceso_usuario")
    usuario = User.objects.filter(~Q(user_permissions=perm))
    perfiles = Perfil.objects.filter(Q(user=usuario[0]))
    for x in range(1, len(usuario)):
        perfiles |= Perfil.objects.filter(Q(user=usuario[x]))
    contexto = {"perfiles": perfiles}
    return render(request, "usuarios/usuario_acceso.html", contexto)


# --- Conceder Acceso al Sistema --- #
#conceder Acceso
@login_required
@permission_required("usuarios.autorizar_usuario", login_url="usuarios:home")
def concederAcceso(request, id_perfil):
    """
    Concede permiso de acceso al sistema y envía un email notificando lo acontecido al usuario
    Recibe el request HTTP y el id del perfil de usuario
    El retorno es una redirección a la página de solicitud
    Requiere inicio de sesión y permisos administrador
    """

    perfil = Perfil.objects.get(id=id_perfil)
    usuario = User.objects.get(id=perfil.user.id)
    perm = Permission.objects.get(codename="acceso_usuario")
    usuario.user_permissions.add(perm)
    send_mail(
        "Solicitud de acceso a SGPA",
        "¡Bienvenido a SGPA! Su solicitud de acceso al sistema fue aceptada",
        settings.EMAIL_HOST_USER,
        [usuario.email],
    )
    return redirect("usuarios:administrador")


# --- Listar Perfiles --- #
#listar perfiles
class ListarPerfil(LoginRequiredMixin, ListView):
    """
    Clase utilizada para listar los perfiles de usuarios existentes
    Hereda de la clase ListView
    Requiere inicio de sesión y permiso de administrador
    """

    redirect_field_name = "redirect_to"
    model = Perfil
    template_name = "usuarios/listar_perfiles.html"


# --- Editar Perfil --- #
#editar perfil admin
@login_required
def editarPerfil_Admin(request, id_perfil):
    """
    Vista para la edición de los datos de un usuario (el email puede ser modificado)
    Recibe el request HTTP y el id del perfil de un usuario
    Devuelve la renderización de la información del usuario
    Requiere inicio de sesión y permiso de administrador
    """

    perfil = Perfil.objects.get(id=id_perfil)
    usuario = User.objects.get(id=perfil.user.id)
    if request.method == "GET":
        perfil_Form = Perfil_Form(instance=perfil)
        usuario_Form = Usuario_Form(instance=usuario)
    else:
        perfil_Form = Perfil_Form(request.POST, instance=perfil)
        usuario_Form = Usuario_Form(request.POST, instance=usuario)
        if all([perfil_Form.is_valid(), usuario_Form.is_valid()]):
            perfil_Form.save(ci=perfil.ci, usuario=usuario, telefono=perfil.telefono)
            usuario_Form.save()
        return redirect("usuarios:listar_perfiles")
    return render(
        request,
        "usuarios/editar_perfil.html",
        {"perfil_Form": perfil_Form, "usuario_Form": usuario_Form},
    )


# --- Eliminar Perfil --- #
#eliminar perfil
@login_required
def eliminarPerfil(request, id_perfil):
    """
    Elimina el perfil del usuario solicitado
    Recibe el request HTTP y el id del perfil de usuario
    Retorna la renderización en el template especificado, en el cual solicita confirmación y luego redirige a la lista de perfiles
    Requiere inicio de sesión y permiso de administrador
    """

    perfil = Perfil.objects.get(id=id_perfil)
    miembro = Miembro.objects.filter(idPerfil=perfil.id)
    if not miembro:
        if request.method == "POST":
            usuario = User.objects.get(id=perfil.user.id)
            usuario.delete()
            perfil.delete()
            return redirect("usuarios:listar_perfiles")
        return render(request, "usuarios/eliminar_perfil.html", {"perfil": perfil})
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "No se puede eliminar al usuario: %s  porque forma parte de un proyecto"
            % perfil.user.first_name,
        )
        return redirect("usuarios:listar_perfiles")
