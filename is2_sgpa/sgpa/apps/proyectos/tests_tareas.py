import pytest
import datetime
from django.contrib.auth.models import User
from usuarios.models import Perfil
from proyectos.models import Proyecto, Sprint, UserStory


@pytest.mark.django_db
def test_crearUserStory():
    # Verifica la creación de un US
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    sprint = Sprint.objects.create(numTareas=1, estado="Iniciado", proyecto=proyecto)

    tarea = UserStory.objects.create(
        nombre="Prueba",
        descripcion="Descripcion",
        fechaCreacion=datetime.date.today(),
        estado="En_Cola",
        desarrollador=perfil,
    )

    assert UserStory.objects.count() == 1
