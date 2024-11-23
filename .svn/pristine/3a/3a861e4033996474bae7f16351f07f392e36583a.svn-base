# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import NivelForms
from .models import Nivel
from .funciones import codificar
from django.db.models import Q


@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    model = Nivel
    nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    data['agregar'] = agregar = request.user.has_perm('{}.add_{}'.format(nombre_app, nombre_model))
    data['editar'] = editar = request.user.has_perm('{}.change_{}'.format(nombre_app, nombre_model))
    data['eliminar'] = eliminar = request.user.has_perm('{}.delete_{}'.format(nombre_app, nombre_model))
    data['ver'] = ver = request.user.has_perm('{}.view_{}'.format(nombre_app, nombre_model))
    data['ruta'] = ruta = request.path
    data['titulo'] = 'Nivel'
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/',"")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'crear':
            try:
                with transaction.atomic():
                    form = NivelForms(request.POST)
                    if form.is_valid():
                        nivel = Nivel(
                                nombre = form.cleaned_data['nombre'],
                                descripcion = form.cleaned_data['descripcion'],
                        )

                        nivel.save(request)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                        return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'editar':
            try:
                form = NivelForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Nivel.objects.get(pk=codificar(request.POST['id']))
                        datos.nombre = form.cleaned_data['nombre']
                        datos.descripcion = form.cleaned_data['descripcion']
                        datos.save(request)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                        return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'eliminar':
            if eliminar:
                try:
                    reg = Nivel.objects.get(pk=codificar(request.POST['id']))
                    reg.estado = False
                    reg.save(request)
                    return JsonResponse({"error": False})
                except Exception as ex:
                    pass
                return HttpResponseRedirect(ruta)
            else:
                messages.error(request, "No tienes permisos para adicionar")
                return redirect('/')
    else:
        if 'pet' in request.GET:
            pet = request.GET['pet']
            if pet == 'crear':
                if agregar:
                    try:
                        data['formTitulo'] = 'Crear nivel'
                        data['form'] = NivelForms()
                        data['pet'] = 'crear'
                        return render(request,'forms/form_menu.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'editar':
                if editar:
                    try:
                        data['formTitulo'] = 'Editar menu'
                        data['pet'] = 'editar'
                        id = request.GET['id']
                        datos = Nivel.objects.get(id=codificar(id))
                        data['reg']= id
                        data['form'] = NivelForms(initial={
                                            'nombre': datos.nombre,
                                            'descripcion': datos.descripcion,
                                        })
                        return render(request,'forms/form_menu.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'eliminar':
                try:
                    with transaction.atomic():
                        men = Nivel.objects.get(id = codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": men.descripcion})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})
        else:
            if ver:
                try:
                    with transaction.atomic():
                        busqueda = None
                        if 's' in request.GET:
                            busqueda = request.GET['s']
                        if busqueda:
                            lista = Nivel.objects.filter(Q(nombre__icontains=busqueda) &Q(estado=True))
                        else:
                            lista = Nivel.objects.filter(estado=True)
                        data['titulo'] = 'Nivel'
                        paginator = Paginator(lista, 6)
                        page_number = request.GET.get('page') or 1
                        obj_pag = paginator.get_page(page_number)
                        pag_act = signing.dumps(int(page_number))
                        paginas = range(1, obj_pag.paginator.num_pages + 1)
                        data['obj_pag'] = obj_pag
                        data['lista'] = obj_pag
                        data['pag_act'] = pag_act
                        data['paginas'] = paginas
                        data['busqueda'] = busqueda if busqueda else ""
                        return render(request, 'vistas/nivel.html', data)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})
            else:
                messages.error(request, "No tienes permisos para visualizar esta información")
                return redirect('/')