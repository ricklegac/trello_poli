from random import randint
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount import providers
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

from usuarios.models import Perfil
from proyectos.models import (
    Proyecto,
    Miembro,
    Rol,
    Sprint,
    TipoUserStory,
    UserStory,
    Columnas,
    Backlog,
    Historial,
)


class Command(BaseCommand):
    def handle(self, *args, **options):

        prov = providers.registry.get_list()
        if not SocialApp.objects.filter(name="Google").exists():
            print("Configurando Google social app")
            sites = Site.objects.all()
            app = SocialApp.objects.create(
                provider=prov[0].id,
                name="Google",
                client_id="694499917440-45fhocd8gvijnojaa17itntpgh00rcj6.apps.googleusercontent.com",
                secret="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",
            )
            app.sites.set(sites)
            app.save()

        if not User.objects.filter(username="admin").exists():
            print("Creando superusuario")
            user = User.objects.create(
                username="admin",
                first_name="admin",
                last_name="admin",
                email="admin@admin.com",
                is_active=True,
                is_staff=True,
                is_superuser=True,
            )
            user.set_password("admin")
            user.save()

        print("Creando usuarios")
        user = User.objects.create(
            username="fulgencio",
            email="fulgencio@gmail.com",
            first_name="Fulgencio",
            last_name="Yegros(Ejemplo)",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        user = User.objects.create(
            username="Jesús",
            email="jesus@gmail.com",
            first_name="Jesús",
            last_name="Gonzalez(Ejemplo)",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        user = User.objects.create(
            username="maria",
            email="maria@gmail.com",
            first_name="Maria",
            last_name="Gomez(Ejemplo)",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        user = User.objects.create(
            username="sofia",
            email="sofia@gmail.com",
            first_name="Sofia",
            last_name="Villamayor(Ejemplo)",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        print("Creando perfiles")
        i = 2
        users = User.objects.all()
        for u in users:
            Perfil.objects.create(
                user=u,
                ci=str(i),
                telefono=None,
            )
            perm = Permission.objects.get(codename="acceso_usuario")
            u.user_permissions.add(perm)
            i += 1

        print("Creando Proyectos")
        #!Finalizado
        perfiles = Perfil.objects.all()
        scrummaster = Perfil.objects.get(id=perfiles[0].id)
        proyecto = Proyecto.objects.create(
            nombre="Proyecto 1 Prueba Finalizado",
            descripcion="Esta es una prueba generada por el script",
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
            scrumMaster=scrummaster,
        )
        Miembro.objects.create(idPerfil=scrummaster, idProyecto=proyecto)
        equipo = Group.objects.create(name="equipo%s" % proyecto.id)
        proyecto.equipo = equipo
        proyecto.save()

        Historial.objects.create(
            operacion="Creacion del Proyecto {}".format(proyecto.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )

        backlog = Backlog.objects.create(
            nombre="Product backlog", proyecto=proyecto, tipo="Product_Backlog"
        )
        backlog.save()
        Historial.objects.create(
            operacion="Creacion del Product Backlog del proyecto {}".format(
                proyecto.nombre
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Backlog",
        )

        # Rol
        nombreRol = "Desarrollador"
        nombreGrupo = "{}{}".format(nombreRol, proyecto.id)
        grupo = Group.objects.create(name=nombreGrupo)
        perms_names = ["Crear user story", "Permite crear un user story"]
        permisos = Permission.objects.filter(name__in=perms_names)
        grupo.permissions.set(permisos)
        rol = Rol.objects.create(
            nombre=nombreRol,
            grupo=grupo,
            proyecto=proyecto,
        )
        Historial.objects.create(
            operacion="Se crea el rol {}".format(rol.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Rol",
        )

        rol.grupo.user_set.add(users[0])
        rol.save()
        Historial.objects.create(
            operacion="Se asigna el rol {} al usuario {}".format(
                rol.nombre, f"{users[0].first_name} {users[0].last_name}"
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Rol",
        )

        tipo_us = TipoUserStory.objects.create(nombre="Estándar", proyecto=proyecto)
        tipo_us.save
        columna1 = Columnas.objects.create(
            nombre="Cancelado", tipo_us=tipo_us, orden=-1
        )
        columna1.save()
        columna2 = Columnas.objects.create(nombre="Inactivo", tipo_us=tipo_us, orden=0)
        columna2.save()
        columna3 = Columnas.objects.create(nombre="To Do", tipo_us=tipo_us, orden=1)
        columna3.save()
        columna4 = Columnas.objects.create(nombre="Doing", tipo_us=tipo_us, orden=2)
        columna4.save()
        columna5 = Columnas.objects.create(nombre="Done", tipo_us=tipo_us, orden=3)
        columna5.save()
        columna6 = Columnas.objects.create(nombre="Relese", tipo_us=tipo_us, orden=-2)
        columna6.save()

        Historial.objects.create(
            operacion="Creacion del tipo de US {}".format(tipo_us.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Tipo User Story",
        )

        sprint = Sprint.objects.create(
            objetivos="Sprint test",
            estado="En_cola",
            proyecto=proyecto,
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
        )
        sprint.estado = "Activo"
        sprint.save()

        Historial.objects.create(
            operacion="Creacion del sprint con objetivo:{} del proyecto {}".format(
                sprint.objetivos, proyecto.nombre
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )

        tarea = UserStory.objects.create(
            nombre="Tarea de Prueba",
            descripcion="generada por el script",
            estado=columna1,
            desarrollador=perfiles[0],
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
            tipo=tipo_us,
            sprint=sprint,
            backlog=backlog,
        )
        tarea.save()
        Historial.objects.create(
            operacion="Creacion del User Story {}".format(tarea.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        tarea.estado = columna2
        tarea.save()
        Historial.objects.create(
            operacion="User Story avanza de estado a {}".format(tarea.estado.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        tarea.estado = columna3
        tarea.save()
        Historial.objects.create(
            operacion="User Story avanza de estado a {}".format(tarea.estado.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        tarea.estado = columna4
        tarea.save()
        Historial.objects.create(
            operacion="User Story avanza de estado a {}".format(tarea.estado.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        sprint.numTareas = 1
        sprint.estado = "Finalizado"
        sprint.save()
        Historial.objects.create(
            operacion="Se completan las tareas del sprint con objetivo:{}".format(
                sprint.objetivos
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Sprint",
        )

        proyecto.estado = "Finalizado"
        proyecto.save()
        Historial.objects.create(
            operacion="Se finaliza el proyecto:{}".format(proyecto.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )

        #!Cancelado
        perfiles = Perfil.objects.all()
        scrummaster = Perfil.objects.get(id=perfiles[0].id)
        proyecto = Proyecto.objects.create(
            nombre="Proyecto 1 Prueba Cancelado",
            descripcion="Esta es una prueba generada por el script",
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
            scrumMaster=scrummaster,
        )
        Miembro.objects.create(idPerfil=scrummaster, idProyecto=proyecto)
        equipo = Group.objects.create(name="equipo%s" % proyecto.id)
        proyecto.equipo = equipo
        proyecto.estado = "Cancelado"
        proyecto.save()
        Historial.objects.create(
            operacion="El proyecto {} se ha cancelado".format(proyecto.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )

        #!Activo
        perfiles = Perfil.objects.all()
        scrummaster = Perfil.objects.get(id=perfiles[0].id)
        proyecto = Proyecto.objects.create(
            nombre="Proyecto 1 Prueba Activo",
            descripcion="Esta es una prueba generada por el script",
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
            scrumMaster=scrummaster,
        )
        Miembro.objects.create(idPerfil=scrummaster, idProyecto=proyecto)
        equipo = Group.objects.create(name="equipo%s" % proyecto.id)
        proyecto.equipo = equipo
        proyecto.save()

        Historial.objects.create(
            operacion="Creacion del Proyecto {}".format(proyecto.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )

        backlog = Backlog.objects.create(
            nombre="Product backlog", proyecto=proyecto, tipo="Product_Backlog"
        )
        backlog.save()
        Historial.objects.create(
            operacion="Creacion del Product Backlog del proyecto {}".format(
                proyecto.nombre
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Backlog",
        )

        # Rol
        nombreRol = "Desarrollador"
        nombreGrupo = "{}{}".format(nombreRol, proyecto.id)
        grupo = Group.objects.create(name=nombreGrupo)
        perms_names = ["Crear user story", "Permite crear un user story"]
        permisos = Permission.objects.filter(name__in=perms_names)
        grupo.permissions.set(permisos)
        rol = Rol.objects.create(
            nombre=nombreRol,
            grupo=grupo,
            proyecto=proyecto,
        )
        Historial.objects.create(
            operacion="Se crea el rol {}".format(rol.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Rol",
        )

        rol.grupo.user_set.add(users[0])
        rol.save()
        Historial.objects.create(
            operacion="Se asigna el rol {} al usuario {}".format(
                rol.nombre, f"{users[0].first_name} {users[0].last_name}"
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Rol",
        )

        tipo_us = TipoUserStory.objects.create(nombre="Default", proyecto=proyecto)
        tipo_us.save
        columna1 = Columnas.objects.create(nombre="To Do", tipo_us=tipo_us)
        columna1.save
        columna2 = Columnas.objects.create(nombre="Doing", tipo_us=tipo_us)
        columna2.save
        columna3 = Columnas.objects.create(nombre="Pending Review", tipo_us=tipo_us)
        columna3.save
        columna4 = Columnas.objects.create(nombre="Done", tipo_us=tipo_us)
        columna4.save

        Historial.objects.create(
            operacion="Creacion del tipo de US {}".format(tipo_us.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Tipo User Story",
        )

        sprint = Sprint.objects.create(
            objetivos="Sprint test",
            estado="En_cola",
            proyecto=proyecto,
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
        )
        sprint.estado = "Activo"
        sprint.save()

        Historial.objects.create(
            operacion="Creacion del sprint con objetivo:{} del proyecto {}".format(
                sprint.objetivos, proyecto.nombre
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )

        tarea = UserStory.objects.create(
            nombre="Tarea de Prueba",
            descripcion="generada por el script",
            estado=columna1,
            desarrollador=perfiles[0],
            fechaCreacion="2022-11-04",
            fechaInicio="2022-11-04",
            fechaFin="2022-11-04",
            tipo=tipo_us,
            sprint=sprint,
            backlog=backlog,
        )
        tarea.save()
        Historial.objects.create(
            operacion="Creacion del User Story {}".format(tarea.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        tarea.estado = columna2
        tarea.save()
        Historial.objects.create(
            operacion="User Story avanza de estado a {}".format(tarea.estado.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        tarea.estado = columna3
        tarea.save()
        Historial.objects.create(
            operacion="User Story avanza de estado a {}".format(tarea.estado.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        tarea.estado = columna4
        tarea.save()
        Historial.objects.create(
            operacion="User Story avanza de estado a {}".format(tarea.estado.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="User Story",
        )

        sprint.numTareas = 1
        sprint.estado = "Finalizado"
        sprint.save()
        Historial.objects.create(
            operacion="Se completan las tareas del sprint con objetivo:{}".format(
                sprint.objetivos
            ),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Sprint",
        )

        proyecto.estado = "Iniciado"
        proyecto.save()
        Historial.objects.create(
            operacion="El proyecto {} se ha iniciado".format(proyecto.nombre),
            autor=perfiles[0].__str__(),
            proyecto=Proyecto.objects.get(id=proyecto.id),
            categoria="Proyecto",
        )
