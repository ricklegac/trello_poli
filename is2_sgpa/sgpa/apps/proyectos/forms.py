from datetime import date, datetime
from django import forms
from django.db.models import Q
from usuarios.models import Perfil
from proyectos.models import Proyecto, Sprint
from django.core.validators import MinValueValidator


class Proyecto_Form(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["nombre", "descripcion", "scrumMaster"]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "scrumMaster": "Scrum Master",
        }

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
            "scrumMaster": forms.Select(attrs={"class": "form-control"}),
        }

    def init(self, args, **kwargs):
        super(Proyecto_Form, self).init(args, **kwargs)
        self.fields["scrumMaster"].queryset = Perfil.objects.filter(~Q(id=1))


class Sprint_Form(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = [
            "objetivos",
            "fechaInicio",
            "fechaFin",
        ]
        labels = {
            "objetivos": "Objetivos",
            "fechaInicio": "Fecha de inicio",
            "fechaFin": "Fecha de finalización",
        }
        widgets = {
            "objetivos": forms.TextInput(attrs={"class": "form-control"}),
            "fechaInicio": forms.DateInput(attrs={"type": "date"}),
            "fechaFin": forms.DateInput(attrs={"type": "date"}),
        }


class ProyectoEdit_Form(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            "nombre",
            "descripcion",
            "estado",
            "fechaFin",
        ]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "estado": "Estado",
            "fechaFin": "Fecha de finalización",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "fechaFin": forms.DateInput(attrs={"type": "date"}),
        }
