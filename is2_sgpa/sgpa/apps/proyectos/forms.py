from django import forms
from django.db.models import Q
from usuarios.models import Perfil
from proyectos.models import (
    Backlog,
    Columnas,
    Miembro,
    Proyecto,
    Rol,
    Sprint,
    TipoUserStory,
    UserStory,
)
from django.contrib.auth.models import Permission
from django.forms import modelformset_factory


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
            "duracion",
        ]
        labels = {
            "objetivos": "Objetivos",
            "duracion": "Duración",
        }
        widgets = {
            "objetivos": forms.TextInput(attrs={"class": "form-control"}),
            "duracion": forms.TextInput(attrs={"class": "form-control"}),
        }


class SprintEdit_Form(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = [
            "objetivos",
            "duracion",
        ]
        labels = {
            "objetivos": "Objetivos",
            "duracion": "Duración",
        }
        widgets = {
            "objetivos": forms.TextInput(attrs={"class": "form-control"}),
            "duracion": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProyectoEdit_Form(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            "nombre",
            "descripcion",
            "fechaFin",
        ]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "fechaFin": "Fecha de finalización",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
            "fechaFin": forms.DateInput(attrs={"type": "date"}),
        }


class MiembrosForm(forms.ModelForm):
    class Meta:
        model = Miembro
        fields = [
            "idPerfil",
        ]
        labels = {
            "idPerfil": "Perfil",
        }
        widgets = {
            "idPerfil": forms.Select(attrs={"class": "form-control custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        perfil = Perfil.objects.all()
        idProyecto = kwargs.pop("idProyecto")
        super(MiembrosForm, self).__init__(*args, **kwargs)
        proyecto = Proyecto.objects.get(id=idProyecto)
        miembro = proyecto.miembro_set.all()
        valid_id = []
        for p in perfil:
            if (
                not Miembro.objects.filter(idProyecto=proyecto)
                .filter(idPerfil=p)
                .exists()
            ):
                if not p.id == 1:
                    valid_id.append(p.id)
        perfiles = Perfil.objects.filter(id__in=valid_id)
        self.fields["idPerfil"].queryset = perfiles


class Rol_Form(forms.ModelForm):
    permissions = [
        "iniciar_proyecto",
        "cancelar_proyecto",
        "crear_proyecto",
        "modificar_proyecto",
        "eliminar_proyecto",
        "crear_sprint",
        "modificar_sprint",
        "eliminar_sprint",
        "iniciar_sprint",
        "cancelar_sprint",
        "finalizar_sprint",
        "crear_user_story",
        "modificar_user_story",
        "eliminar_user_story",
        "crear_rol",
        "modificar_rol",
        "eliminar_rol",
        "asignar_desasignar_rol",
        "agregar_miembros",
        "eliminar_miembros",
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
        # self.fields["sprint"].queryset = Sprint.objects.filter(
        #     proyecto=proyecto
        # ).order_by("id")
        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            lista = instance.grupo.permissions.all().values_list("name", "codename")
            self.fields["select"].initial = [x[0] for x in lista]

    class Meta:
        model = Rol
        fields = ["nombre"]
        labels = {"nombre": "Nombre"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserStoryForm(forms.ModelForm):
    def __init__(self, idProyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tipos = TipoUserStory.objects.filter(proyecto=idProyecto).order_by("id")
        backlogs = Backlog.objects.filter(proyecto=idProyecto)
        # sprints = (
        #     Sprint.objects.filter(proyecto=idProyecto)
        #     .order_by("posicion")
        #     .exclude(estado="Cancelado")
        #     .exclude(estado="Finalizado")
        # )
        desarroladores = Perfil.objects.filter(miembros__idProyecto=idProyecto)
        self.fields["tipo"].queryset = tipos
        self.fields["tipo"].initial = tipos.first()
        self.fields["backlog"].queryset = backlogs
        self.fields["backlog"].initial = backlogs.first()
        self.fields["desarrollador"].queryset = desarroladores
        # self.fields["sprint"].queryset = sprints
        # self.fields["sprint"].initial = sprints.first()

    class Meta:
        model = UserStory
        fields = [
            "backlog",
            "nombre",
            "descripcion",
            "estado",
            "desarrollador",
            "horas_estimadas",
            "tipo",
            "prioridad_tecnica",
            "prioridad_funcional",
        ]
        labels = {
            "backlog": "Backlog",
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "desarrollador": "Desarrollador",
            "horas_estimadas": "Horas estimadas",
            "tipo": "Tipo",
            "prioridad_tecnica": "Prioridad técnica",
            "prioridad_funcional": "Prioridad funcional",
        }
        widgets = {
            "backlog": forms.Select(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "desarrollador": forms.Select(attrs={"class": "form-control"}),
            "horas_estimadas": forms.NumberInput(
                {"class": "form-control col-3", "min": "0"}
            ),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "prioridad_funcional": forms.NumberInput(
                {"class": "form-control col-3", "min": "1", "max": "10"}
            ),
            "prioridad_tecnica": forms.NumberInput(
                {"class": "form-control col-3", "min": "1", "max": "10"}
            ),
        }


class UserStoryEdit_Form(forms.ModelForm):
    def __init__(self, idProyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tipos = TipoUserStory.objects.filter(proyecto=idProyecto).order_by("id")
        # sprints = (
        #     Sprint.objects.filter(proyecto=idProyecto)
        #     .order_by("posicion")
        #     .exclude(estado="Cancelado")
        #     .exclude(estado="Finalizado")
        # )
        self.fields["tipo"].queryset = tipos
        # self.fields["sprint"].queryset = sprints

    class Meta:
        model = UserStory
        fields = [
            "nombre",
            "descripcion",
            "prioridad",
            "desarrollador",
            "horas_trabajadas",
            "horas_estimadas",
            "tipo",
            "prioridad_tecnica",
            "prioridad_funcional",
        ]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripcion",
            "prioridad": "Prioridad",
            "desarrollador": "Desarrollador",
            "horas_estimadas": "Horas estimadas",
            "horas_trabajadas": "Horas trabajadas",
            "tipo": "Tipo",
            "prioridad_tecnica": "Prioridad técnica",
            "prioridad_funcional": "Prioridad funcional",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "prioridad": forms.TextInput(attrs={"class": "form-control"}),
            "desarrollador": forms.Select(attrs={"class": "form-control"}),
            "fechaInicio": forms.DateInput(attrs={"type": "date"}),
            "horas_estimadas": forms.TextInput(attrs={"class": "form-control"}),
            "horas_trabajadas": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "prioridad_funcional": forms.NumberInput(
                {"class": "form-control col-3", "min": "1", "max": "10"}
            ),
            "prioridad_tecnica": forms.NumberInput(
                {"class": "form-control col-3", "min": "1", "max": "10"}
            ),
        }


class TipoUserStoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            id = kwargs.pop("id")
            proyecto = Proyecto.objects.get(id=id)
            self.proyecto = proyecto
        except:
            pass
        super(TipoUserStoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        proyecto = kwargs.get("proyecto")
        instance = super(TipoUserStoryForm, self).save(commit=False)
        instance.proyecto = proyecto
        if commit:
            instance.save()
        return instance

    class Meta:
        model = TipoUserStory
        fields = [
            "nombre",
        ]
        labels = {
            "nombre": "Nombre",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
        }


AdicionalColumnaFormset = modelformset_factory(
    Columnas,
    fields=("nombre", "opcional"),
    extra=1,
    widgets={
        "nombre": forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "max-width: 50%",
                "placeholder": "Ingrese nombre de la columna",
            },
        ),
        "opcional": forms.CheckboxInput(),
    },
)


# class ColumnasForm(forms.ModelForm):
#     class Meta:
#         model = Columnas
#         fields = [
#             "nombre",
#         ]
#         labels = {
#             "nombre": "Nombre",
#         }
#         widgets = {
#             "nombre": forms.TextInput(attrs={"class": "form-control"}),
#         }


class KanbanForm(forms.ModelForm):
    def __init__(self, idProyecto, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tipos = TipoUserStory.objects.filter(proyecto=idProyecto).order_by("id")
        self.fields["tipo"].queryset = tipos
        self.fields["tipo"].initial = tipos.first()

    class Meta:
        model = UserStory
        fields = [
            "nombre",
            "tipo",
        ]
        labels = {
            "nombre": "Nombre",
            "tipo": "Tipo",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
        }
