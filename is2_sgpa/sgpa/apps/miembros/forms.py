from usuarios.models import Perfil
from proyectos.models import Proyecto
from django import forms
from django.forms import widgets
from miembros.models import Miembro


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
