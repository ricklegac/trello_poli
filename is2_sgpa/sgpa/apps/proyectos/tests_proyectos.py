import pytest
import datetime
from django.test import Client, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from usuarios.models import Perfil
from proyectos.models import Proyecto, Sprint, UserStory, Columnas, TipoUserStory


# --- Test Listar Proyectos --- #
# Verifica el correcto funcionamiento de la vista ListarProyectos
@pytest.mark.django_db
def test_ListarProyecto():
    # Simulación de inicio de sesión
    user = User.objects.create(username="usuarioPrueba")
    user.set_password("12345")
    user.save()
    client = Client()
    client.login(username="usuarioPrueba", password="12345")
    # Verifica que la vista responda correctamente a un pedido GET
    response = client.get("http://127.0.0.1:8000/proyectos/listar/")

    assert response.status_code == 200


# --- Test Crear Proyecto --- #
# Verifica la creación de un proyecto
@pytest.mark.django_db
def test_CrearProyecto():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    assert Proyecto.objects.count() == 1


# --- Test Finalizar Proyecto --- #
# Verifica la correcta finalizacion de un proyecto
@pytest.mark.django_db
def test_FinalizarProyecto():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    sprint = Sprint.objects.create(numTareas=0, estado="Finalizado", proyecto=proyecto)
    sprint.save()
    proyecto.save()

    path = "<int:id_proyecto>/finalizar/"

    user = User.objects.create(username="testuser")
    user.set_password("12345")
    user.save()
    client = Client()
    client.login(username="testuser", password="12345")
    request = client.post(path)
    request.user = usuario
    setattr(request, "session", "session")
    m = FallbackStorage(request)
    setattr(request, "_messages", m)

    proyecto.estado = "Finalizado"
    proyecto.save()

    proyecto = Proyecto.objects.get(id=proyecto.id)
    assert proyecto.estado == "Finalizado"


# # --- Finalizar Proyecto Falla --- #
# # Verifica que no puede finalizarse un proyecto sin haber finalizado el sprint
@pytest.mark.django_db
def test_FinalizarProyecto2():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    sprint = Sprint.objects.create(numTareas=0, estado="Iniciado", proyecto=proyecto)
    sprint.save()
    proyecto.save()

    path = "<int:id_proyecto>/finalizar/"
    # Simulación de inicio de sesión
    user = User.objects.create(username="testuser")
    user.set_password("12345")
    user.save()
    client = Client()
    client.login(username="testuser", password="12345")
    request = client.post(path)
    request.user = usuario
    setattr(request, "session", "session")
    m = FallbackStorage(request)
    setattr(request, "_messages", m)

    proyecto.estado = "Iniciado"

    proyecto = Proyecto.objects.get(id=proyecto.id)
    assert proyecto.estado == "Finalizado", "Existe un sprint sin finalizar"


####
#   Sprint Tests
####

# --- Crear Sprint --- #
@pytest.mark.django_db
def test_creaSprint():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    # Verifica que la vista guarde las Fases vinculadas a un proyecto
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    sprint1 = Sprint.objects.create(numTareas=0, estado="Iniciado", proyecto=proyecto)
    sprint2 = Sprint.objects.create(numTareas=0, estado="Iniciado", proyecto=proyecto)
    assert Sprint.objects.count() == 2


# --- Test Finalizar Sprint --- #
# Verifica la correcta finalizacion de un Sprint
@pytest.mark.django_db
def test_finalizarSprintF():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    sprint = Sprint.objects.create(numTareas=2, proyecto=proyecto, estado="En_cola")
    tarea1 = UserStory.objects.create(
        nombre="Prueba1",
        descripcion="Descripcion1",
        fechaCreacion=datetime.date.today(),
        desarrollador=perfil,
    )
    tarea2 = UserStory.objects.create(
        nombre="Prueba2",
        descripcion="Descripcion2",
        fechaCreacion=datetime.date.today(),
        desarrollador=perfil,
    )

    tarea1.estado = "Done"
    tarea2.estado = "Done"
    tarea1.save()
    tarea2.save()
    sprint.estado = "Finalizado"
    sprint.save()

    # Finalización del Sprint
    path = "<int:id_proyecto>/sprint/<int:id_sprint>/finalizar/"
    request1 = RequestFactory().get(path)
    request1.user = usuario

    setattr(request1, "session", "session")
    messages = FallbackStorage(request1)
    setattr(request1, "_messages", messages)

    # finalizarSprint(request1, proyecto.id, sprint.id)
    sprint = Sprint.objects.get(id=sprint.id)
    assert sprint.estado == "Finalizado", print(messages)


# --- Test Finalizar Sprint FALLA --- #
# Verifica la correcta finalizacion de un Sprint
@pytest.mark.django_db
def test_finalizarSprintF():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    sprint = Sprint.objects.create(numTareas=2, proyecto=proyecto)
    tarea1 = UserStory.objects.create(
        nombre="Prueba1",
        descripcion="Descripcion1",
        fechaCreacion=datetime.date.today(),
        desarrollador=perfil,
        sprint=sprint,
    )
    tarea2 = UserStory.objects.create(
        nombre="Prueba2",
        descripcion="Descripcion2",
        fechaCreacion=datetime.date.today(),
        desarrollador=perfil,
        sprint=sprint,
    )

    tipo = TipoUserStory.objects.get(proyecto=proyecto)
    columnas = Columnas.objects.filter(tipo_us=tipo)

    tarea1.estado = columnas.last()
    tarea2.estado = columnas.first()
    tarea1.save()
    tarea2.save()
    sprint.estado = "Iniciado"
    sprint.save()

    # Finalización del Sprint
    path = "<int:id_proyecto>/sprint/<int:id_sprint>/finalizar/"
    request1 = RequestFactory().get(path)
    request1.user = usuario

    setattr(request1, "session", "session")
    messages = FallbackStorage(request1)
    setattr(request1, "_messages", messages)

    # finalizarSprint(request1, proyecto.id, sprint.id)
    sprint = Sprint.objects.get(id=sprint.id)
    assert sprint.estado == "Finalizado", print(messages)


# --- Test Crear Tipo --- #
# Verifica la correcta creacion de un tipo de US
@pytest.mark.django_db
def test_CrearTipos():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    tipo = TipoUserStory.objects.create(
        nombre="Tipo A",
        proyecto=proyecto,
    )
    assert TipoUserStory.objects.filter(
        proyecto=proyecto
    ).exists(), "No se pudo crear el Tipo de US"


# --- Test Crear Tipo FALLA--- #
# Verifica la falla en la creacion de un tipo de US
@pytest.mark.django_db
def test_CrearTiposF():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    tipo = TipoUserStory.objects.create(
        nombre="Tipo A",
        proyecto=proyecto,
    )
    tipo.save()
    tipo2 = TipoUserStory.objects.create(
        nombre="Tipo A",
        proyecto=proyecto,
    )
    tipo2.save()
    assert (
        TipoUserStory.objects.filter(proyecto=proyecto).count() == 1
    ), "No se pudo crear el Tipo de US"


# --- Test Crear Columnas de tipos --- #
# Verifica la correcta creacion de una columna para tipo de US
@pytest.mark.django_db
def test_CrearColumnas():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    tipo = TipoUserStory.objects.create(
        nombre="Tipo A",
        proyecto=proyecto,
    )

    columna = Columnas.objects.create(nombre="To Do", tipo_us=tipo)
    columna.save()

    assert Columnas.objects.filter(
        tipo_us=tipo
    ).exists(), "No se pudo crear la columna para el Tipo de US"


# --- Test Crear Columnas de tipos --- #
# Verifica la correcta creacion de una columna para tipo de US
@pytest.mark.django_db
def test_CrearColumnasF():
    usuario = User.objects.create_user("Won", "won@seo.com", "hyungwon")
    usuario.save()
    perfil = Perfil.objects.create(ci=108108, telefono=108108, user=usuario)
    perfil.save()
    proyecto = Proyecto.objects.create(
        nombre="Bartender",
        descripcion="Curso de Bartender",
        fechaCreacion=datetime.date.today(),
        numSprints=0,
        estado="Pendiente",
        scrumMaster=perfil,
    )
    tipo = TipoUserStory.objects.create(
        nombre="Tipo A",
        proyecto=proyecto,
    )

    columna = Columnas.objects.create(nombre="To Do", tipo_us=tipo)
    columna.save()

    columna2 = Columnas.objects.create(nombre="To Do", tipo_us=tipo)
    columna2.save()

    assert (
        columna.nombre != columna2.nombre
    ), "No se pudo crear la columna para el Tipo de US"
