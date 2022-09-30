from django import forms
from django.db.models import Q
from miembros.models import Miembro
from usuarios.models import Perfil
from tareas.models import UserStory
from django.forms import Form, CharField, IntegerField


class UserStoryForm(Form):
    nombre = CharField()
    descripcion = CharField()
    prioridad = IntegerField()


class UserStoryEdit_Form(forms.ModelForm):
    class Meta:
        model = UserStory
        fields = [
            "nombre",
            "descripcion",
            "estado",
            "desarrollador",
        ]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "estado": "Estado",
            "desarrollador": "Desarrollador",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "desarrollador": forms.Select(attrs={"class": "form-control"}),
        }

        def init(self, args, **kwargs):
            super(UserStoryEdit_Form, self).init(args, **kwargs)
            self.fields["desarrollador"].queryset = Miembro.objects.filter(~Q(id=1))
