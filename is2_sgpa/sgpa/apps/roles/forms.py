from django import forms
from roles.models import Rol
from django.forms import widgets
from proyectos.models import Proyecto, Sprint
from django.contrib.auth.models import Permission


class Rol_Form(forms.ModelForm):
    permissions = [
        "Crear proyecto",
        "Modificar proyecto",
        "Eliminar proyecto",
        "Crear Sprint",
        "Modificar Sprint",
        "Cancelar Sprint",
        "Crear user story",
        "Modificar user story" "Eliminar user story",
    ]
    permisos = Permission.objects.filter(codename__in=permissions).values_list(
        "name", "codename"
    )
    select = forms.MultipleChoiceField(
        choices=permisos, widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        id = kwargs.pop("idProyecto")
        super(Rol_Form, self).__init__(*args, **kwargs)
        proyecto = Proyecto.objects.get(id=id)
        self.fields["sprint"].queryset = Sprint.objects.filter(
            proyecto=proyecto
        ).order_by("id")
        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            lista = instance.grupo.permissions.all().values_list("name", "codename")
            self.fields["select"].initial = [x[0] for x in lista]

    class Meta:
        model = Rol
        fields = ["nombre", "sprint"]
        labels = {"nombre": "Nombre", "sprint": "Sprint"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "sprint": forms.CheckboxSelectMultiple(),
        }
