from random import randint
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from allauth.socialaccount.models import SocialApp, SocialAccount
from allauth.socialaccount import providers
from django.contrib.sites.models import Site


from usuarios.models import Perfil


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
            last_name="Yegros",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        user = User.objects.create(
            username="Jesús",
            email="jesus@gmail.com",
            first_name="Jesús",
            last_name="Gonzalez",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        print("Creando perfiles")
        i = 2
        for u in User.objects.all():
            Perfil.objects.create(
                user=u,
                ci=str(i),
                telefono=None,
            )
            perm = Permission.objects.get(codename="acceso_usuario")
            u.user_permissions.add(perm)
            i += 1
