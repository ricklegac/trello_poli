import pytest
from django.test import TestCase
from usuarios.models import Perfil
from usuarios.forms import Usuario_Form, Perfil_Form
from django.contrib.auth.models import User


# --- Verifica la creación de usuario --- #
#test crear usuario
@pytest.mark.django_db
def test_crearUsuario():
    data = {
        "first_name": "Lorenzo",
        "last_name": "Cabrera",
        "email": "lorenzocabrea8@fpuna.edu.py",
    }
    form = Usuario_Form(data=data)
    assert form.is_valid() is True, form.errors


# --- Verifica la eliminación de un usuario --- #
#test eliminar usuario
@pytest.mark.django_db
def test_eliminarUsuario():
    data = {
        "firs_name": "Lorenzo",
        "last_name": "Cabrera",
        "email": "lorenzocabrea8@fpuna.edu.py",
    }
    form = Usuario_Form(data=data)
    form.save()
    usuario = User.objects.get(email="lorenzocabrea8@fpuna.edu.py")
    usuario.delete()
    assert not User.objects.filter(email="lorenzocabrea8@fpuna.edu.py").exists()


# --- Verifica la creación de un perfil de usuario --- #
#test crear perfil
@pytest.mark.django_db
def test_crearPerfil():
    data = {
        "firs_name": "Lorenzo",
        "last_name": "Cabrera",
        "email": "lorenzocabrea8@fpuna.edu.py",
    }
    form = Usuario_Form(data=data)
    form.save()
    usuario = User.objects.get(email="lorenzocabrea8@fpuna.edu.py")
    data = {
        "user": usuario,
        "ci": 4177075,
        "telefono": "0982186022",
    }
    perfil_Form = Perfil_Form(data=data)
    assert perfil_Form.is_valid() is True, perfil_Form.errors


# FALLA
# --- Verifica que no se pueden crear dos perfiles con el mismo ci --- #
#test crear segundo perfil
@pytest.mark.django_db
def test_crearSegundoPerfil():
    data = {
        "firs_name": "Carlos",
        "last_name": "Perez",
        "email": "asd@fpuna.edu.py",
    }
    form = Usuario_Form(data=data)
    form.save()
    usuario = User.objects.get(email="asd@fpuna.edu.py")
    data = {
        "user": usuario,
        "ci": 41770756,
        "telefono": "0498212",
    }
    perfil_Form = Perfil_Form(data=data)
    if perfil_Form.is_valid():
        perfil_Form.save(ci=41770756, usuario=usuario, telefono="0498212")

    perfil_Form = Perfil_Form(data=data)
    if perfil_Form.is_valid():
        perfil_Form.save(ci=41770756, usuario=usuario, telefono="0498212")

    assert perfil_Form.is_valid() is True, perfil_Form.errors


# --- Verifica la eliminarción de un perfil de usuario --- #
#test eliminar perfil
@pytest.mark.django_db
def test_eliminarPerfil():
    data = {
        "firs_name": "Lorenzo",
        "last_name": "Cabrera",
        "email": "lorenzocabrea8@fpuna.edu.py",
    }
    form = Usuario_Form(data=data)
    form.save()
    usuario = User.objects.get(email="lorenzocabrea8@fpuna.edu.py")
    data = {
        "user": usuario,
        "ci": 4177075,
        "telefono": "0982186022",
    }
    perfil_Form = Perfil_Form(data=data)
    if perfil_Form.is_valid():
        perfil_Form.save(ci=4177075, usuario=usuario, telefono="0982186022")
    perfil = Perfil.objects.get(ci=4177075)
    perfil.delete()
    assert not Perfil.objects.filter(ci=4177075).exists()
