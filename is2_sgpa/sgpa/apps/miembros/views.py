from usuarios.models import Perfil
from miembros.models import Miembro
from proyectos.models import Proyecto, Historial
from miembros.forms import MiembrosForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

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

        return redirect("miembros:listar", idProyecto=idProyecto)

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
        return redirect("miembros:listar", idProyecto=idProyecto)
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
