from django import forms
from django.contrib.auth.models import User
from .models import Perfil


class Perfil_Form(forms.ModelForm):
    def save(self, commit=True, *args, **kwargs):
        ci = kwargs.get("ci")
        usuario = kwargs.get("usuario")
        telefono = kwargs.get("telefono")
        instance = super(Perfil_Form, self).save(commit=False)
        instance.ci = ci
        instance.user = usuario
        instance.telefono = telefono
        if commit:
            instance.save()

    class Meta:
        model = Perfil
        fields = [
            "ci",
            "telefono",
        ]
        labels = {
            "ci": "CI",
            "telefono": "Teléfono",
        }
        widgets = {
            "ci": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su número de CI",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su número de teléfono",
                }
            ),
        }


class Usuario_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Email",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(
                attrs={"class": "form-control", "readonly": "readonly"}
            ),
        }


class PerfilEdit_Form(forms.ModelForm):
    def save(self, commit=True, *args, **kwargs):
        usuario = kwargs.get("usuario")
        telefono = kwargs.get("telefono")
        instance = super(PerfilEdit_Form, self).save(commit=False)
        instance.user = usuario
        instance.telefono = telefono
        if commit:
            instance.save()

    class Meta:
        model = Perfil
        fields = [
            "ci",
            "telefono",
        ]
        labels = {
            "ci": "CI",
            "telefono": "Teléfono",
        }
        widgets = {
            "ci": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su número de CI",
                    "readonly": "readonly",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su número de teléfono",
                }
            ),
        }
