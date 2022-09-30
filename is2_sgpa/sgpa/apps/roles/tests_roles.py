import pytest
import datetime
from proyectos.models import Proyecto
from usuarios.models import User, Perfil
from django.contrib.auth.models import Group
from roles.models import Rol
from django.urls import reverse

# --- Crear Grupo --- #
# Verifica la creación de un grupo
@pytest.mark.django_db
def test_CrearGrupo():
    Group.objects.create(name="Team")
    assert Group.objects.count() == 1


# --- Eliminar Grupo --- #
# Verifica la eliminación de un grupo
@pytest.mark.django_db
def test_EliminarGrupo():
    grupo = Group.objects.create(name="Team")
    grupo.delete()
    assert Group.objects.count() == 0


# --- Eliminar Rol --- #
# Verifica la eliminación de un rol
@pytest.mark.django_db
def test_EliminarRol():
    grupo = Group.objects.create(name="Team")
    rol = Rol.objects.create(nombre="Rol", grupo=grupo)
    rol.delete()
    assert Rol.objects.count() == 0


# --- Eliminar Rol Falla --- #
# Verifica que un rol que no existe no puede ser eliminado
@pytest.mark.django_db
def test_EliminarRol2():
    grupo = Group.objects.create(name="Team")
    rol = Rol.objects.create(nombre="Rol", grupo=grupo)
    try:
        rol.delete()
        rol.delete()
    except:
        assert False, "No se puede eliminar un rol que no existe"


# --- Crear Rol --- #
@pytest.mark.django_db
def test_CrearRol():
    grupo = Group.objects.create(name="Team")
    Rol.objects.create(nombre="Rol", grupo=grupo)
    assert Rol.objects.count() == 1


# --- Crear Rol Falla --- #
# Verifica que no se puedan crear roles con el mismo nombre
@pytest.mark.django_db
def test_CrearRol2():
    grupo1 = Group.objects.create(name="Team1")
    grupo2 = Group.objects.create(name="Team2")
    usuario = User.objects.create_user("Ezequiel", "eze@lopez.com", "ezelopez")
    perfil = Perfil.objects.create(ci=4351785, telefono=1548795, user=usuario)
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    try:
        Rol.objects.create(nombre="Rol", grupo=grupo1, proyecto=proyecto)
        Rol.objects.create(nombre="Rol", grupo=grupo2, proyecto=proyecto)
    except:
        assert False, "No se permiten roles con el mismo nombre en un mismo proyecto"
