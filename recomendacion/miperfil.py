# -*- coding: UTF-8 -*-
from django.contrib.auth.models import *
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.template import Context
from django.template.loader import get_template

from .forms import PersonaForms, deshabilitar_campo
from .models import Persona
from .funciones import codificar
from datetime import datetime
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    # model = Menu
    # nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    # data['agregar'] = agregar = request.user.has_perm('{}.add_{}'.format(nombre_app, nombre_model))
    # data['editar'] = editar = request.user.has_perm('{}.change_{}'.format(nombre_app, nombre_model))
    # data['eliminar'] = eliminar = request.user.has_perm('{}.delete_{}'.format(nombre_app, nombre_model))
    # data['ver'] = ver = request.user.has_perm('{}.view_{}'.format(nombre_app, nombre_model))
    data['ruta'] = ruta = request.path
    data['titulo'] = 'Mi perfil'
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/',"")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""

    if request.method == 'POST':
        pet = request.POST['pet']

        if pet == 'editar':
            try:
                form = PersonaForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Persona.objects.get(pk=codificar(request.POST['id']))
                        datos.sexo = form.cleaned_data['sexo']
                        datos.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                        datos.correo = form.cleaned_data['correo']

                        if 'foto' in request.FILES:
                            datos.foto = request.FILES['foto']

                        datos.save(request)
                        request.session['persona'] = Persona.objects.get(usuario=request.user)

                        user = User.objects.get(pk=datos.usuario.pk)
                        user.email = datos.correo
                        user.save()
                        print(ruta)
                        return JsonResponse({"error": False, "to": ruta})
                    # else:
                    #     raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta,'msj': 'error al guardar los datos'})

        if pet == 'cambiarContraseña':
            try:
                with transaction.atomic():
                    usuario = User.objects.get(id=request.user.id)
                    old_password= request.POST['old_password']
                    if usuario.check_password(old_password):

                        usuario.set_password(request.POST['password'])
                        usuario.save()
                        update_session_auth_hash(request, usuario)  # Important!
                        messages.success(request, 'Su contraseña ha sido actualizada')
                        return JsonResponse({"error": False, "to": ruta, 'msj': 'Su contraseña ha sido actualizada'})
                    else:
                        return JsonResponse({"error": True, "to": ruta, 'msj': 'La contraseña actual no es la correcta'})

            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta,'msj':'Algo ha salido mal'})

    else:
        if 'pet' in request.GET:
            pet = request.GET['pet']

            if pet == 'editar':
                try:
                    with transaction.atomic():
                        data['pet'] = 'editar'
                        id = request.GET['id']
                        datos = Persona.objects.get(id=codificar(id))
                        data['reg'] = id
                        data['formPerfil'] = form = PersonaForms(initial={
                            'nombres': datos.nombres,
                            'apellidos': datos.apellidos,
                            'sexo': datos.sexo,
                            'cedula': datos.cedula,
                            'fecha_nacimiento': datos.fecha_nacimiento,
                            'correo': datos.correo,
                            'foto': datos.foto,
                        })
                        deshabilitar_campo(form, 'cedula')
                        deshabilitar_campo(form, 'nombres')
                        deshabilitar_campo(form, 'apellidos')

                        return render(request, 'vistas/editmiperfil.html', data)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})
        else:
            try:
                with transaction.atomic():



                    return render(request, 'vistas/miperfil.html', data)

            except Exception as ex:
                transaction.set_rollback(True)
                return redirect('/')
