from django import forms
from datetime import datetime, timedelta
from django.forms.widgets import DateTimeInput,CheckboxInput
from .models import *
import os


class ExtFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        upload = super(ExtFileField, self).clean(*args, **kwargs)
        if upload:
            size = upload.size
            filename = upload.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if size == 0 or ext not in self.ext_whitelist or size > self.max_upload_size:
                raise forms.ValidationError("Tipo de archivo o tamaño no permitido.")


def deshabilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True
    # form.fields[campo].widget.attrs['disabled'] = True


class MenuForms(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    descripcion = forms.CharField(label="Descripción", max_length=140, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    ruta = forms.CharField(label="Ruta", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    es_principal = forms.BooleanField(label='Es principal?', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control form-check-input', 'col': '6'}))
    principal = forms.ModelChoiceField(label="Principal", required=False, queryset=Menu.objects.filter(estado=True, es_principal=True, principal__isnull= True),widget=forms.Select(attrs={'class': 'form-control select', 'col': '6'}))
    acceso = forms.ModelMultipleChoiceField(label="Acceso a perfil", required=False, queryset=Group.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'form-control select', 'col': '6'}))
    icono = forms.ImageField(label="Icono", required=False)


class PerfilForms(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PerfilForms, self).__init__(*args, **kwargs)
        self.fields['permissions'].widget = forms.SelectMultiple()
        self.fields['permissions'].widget.attrs['class'] = "form-control dual"
        self.fields['permissions'].queryset = Permission.objects.exclude(content_type__model__in=['session', 'user', 'permission', 'contenttype', 'logentry', 'configuracion']).order_by('name')
        for k, v in self.fields.items():
            if k in ('name',):
                self.fields[k].widget.attrs['oninput'] = "mayus(this);"
            if not k in ('permissions',):
                self.fields[k].widget.attrs['class'] = "form-control"
                self.fields[k].widget.attrs['placeholder'] = "Inserte {}".format(self.fields[k].label)


class PersonaForms(forms.Form):
    cedula=forms.CharField(label="Cédula", max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '2'}))
    nombres = forms.CharField(label="Nombres", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '5'}))
    apellidos = forms.CharField(label="Apellidos", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '5'}))
    sexo = forms.ChoiceField(choices=tipo_sexo, initial=1, label=u'Sexo', required=False, widget=forms.Select(attrs={'class': 'form-control sm','col':'4'}))
    fecha_nacimiento = forms.DateField(label="Fecha Nacimiento", initial=datetime.now().date(), input_formats=['%d-%m-%Y'], widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'datepicker form-control sm', 'col': '4'}), required=False)
    correo = forms.EmailField(label="Correo", max_length=140, required=False,widget=forms.EmailInput(attrs={'class': 'form-control', 'col': '6'}))
    foto = forms.ImageField(label="Foto", required=False)


class SitioForms(forms.Form):
    nombresitio = forms.CharField(label="Nombre Sitio", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    correo = forms.EmailField(label="Correo", max_length=140, required=True,widget=forms.EmailInput(attrs={'class': 'form-control', 'col': '6'}))
    clave = forms.CharField(label="Clave de terceros", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    icono = forms.ImageField(label="Icono", required=False)
    favicono = forms.ImageField(label="Favicon", required=False)

class CambiarClaveForms(forms.Form):
    contraseña1 = forms.CharField(label="Nueva contraseña", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))
    contraseña2 = forms.CharField(label="Confirmar contraseña", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))

class NivelForms(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    descripcion = forms.CharField(label="Descripción", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))

class AsignaturaForms(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    descripcion = forms.CharField(label="Descripción", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    nivel = forms.ModelChoiceField(label="Nivel académico", required=False,queryset=Nivel.objects.filter(estado=True),widget=forms.Select(attrs={'class': 'form-control select', 'col': '6'}))
    imagen = forms.ImageField(label="Imagen", required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'col': '6'}))

class ContenidoForms(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '12'}))
    descripcion = forms.CharField(label="Descripción", max_length=140, required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'col': '12'}))


class EjercicioForms(forms.Form):
    asignatura = forms.ModelChoiceField(label="Asignatura", required=False, queryset=Asignatura.objects.filter(estado=True),widget=forms.Select(attrs={'class': 'form-control select', 'col': '6'}))
    contenido = forms.ModelMultipleChoiceField(label="Contenido", required=False, queryset=Contenido.objects.filter(estado=True),widget=forms.SelectMultiple(attrs={'class': 'form-control select', 'col': '6'}))
    nombre = forms.CharField(label="Nombre", max_length=140, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'col': '12'}))
    descripcion = forms.CharField(label="Descripción", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'col': '12','id':'elm1'}))
    dificultad = forms.CharField(label="Dificultad", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '12'}))

class EvaluacionForms(forms.Form):
    archivo = forms.FileField(label="Archivo",required=False,widget=forms.FileInput(attrs={'class': 'form-control', 'col': '12'}))
    gusto = forms.CharField(label="Gusto", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    dificultad = forms.CharField(label="Dificultad", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    ejercicio = forms.CharField(label="Ejercicio", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))
    duracion = forms.CharField(label="Duración", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '6'}))

class RegistroForms(forms.Form):
    nombres = forms.CharField(label="Nombres", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '5'}))
    apellidos = forms.CharField(label="Apellidos", max_length=140, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '5'}))
    sexo = forms.ChoiceField(choices=tipo_sexo, initial=1, label=u'Sexo', required=False,widget=forms.Select(attrs={'class': 'form-control sm', 'col': '4'}))
    fecha_nacimiento = forms.DateField(label="Fecha Nacimiento", initial=datetime.now().date(),input_formats=['%d-%m-%Y'], widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'datepicker form-control sm', 'col': '4','placeholder':'dd-mm-aaaa'}), required=False)
    usuario = forms.CharField(label="Usuario", max_length=10, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'col': '2'}))
    contraseña = forms.CharField(label="Contraseña", max_length=10, required=True,widget=forms.PasswordInput(attrs={'class': 'form-control', 'col': '6'}))