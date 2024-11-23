# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import MenuForms
from .models import Menu
from .funciones import codificar
from django.db.models import Q


@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    model = Menu
    nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    data['agregar'] = agregar = request.user.has_perm('{}.add_{}'.format(nombre_app, nombre_model))
    data['editar'] = editar = request.user.has_perm('{}.change_{}'.format(nombre_app, nombre_model))
    data['eliminar'] = eliminar = request.user.has_perm('{}.delete_{}'.format(nombre_app, nombre_model))
    data['ver'] = ver = request.user.has_perm('{}.view_{}'.format(nombre_app, nombre_model))
    data['ruta'] = ruta = request.path
    data['titulo'] = 'Módulos'
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/',"")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'crear':
            try:
                with transaction.atomic():
                    form = MenuForms(request.POST)
                    if form.is_valid():
                        menu = Menu(
                                nombre = form.cleaned_data['nombre'],
                                descripcion = form.cleaned_data['descripcion'],
                                ruta = form.cleaned_data['ruta'],
                                es_principal = form.cleaned_data['es_principal'],
                                principal = form.cleaned_data['principal'],
                        )
                        if 'icono' in request.FILES:
                            menu.icono = request.FILES['icono']
                        menu.save(request)

                        acceso = form.cleaned_data.get("acceso")
                        for x in acceso:
                            menu.acceso.add(x)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                         return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'editar':
            try:
                form = MenuForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Menu.objects.get(pk=codificar(request.POST['id']))
                        datos.nombre = form.cleaned_data['nombre']
                        datos.descripcion = form.cleaned_data['descripcion']
                        if 'icono' in request.FILES:
                            datos.icono = request.FILES['icono']
                        datos.ruta = form.cleaned_data['ruta']
                        datos.es_principal = form.cleaned_data['es_principal']
                        datos.principal = form.cleaned_data['principal']
                        datos.save(request)
                        acceso = form.cleaned_data.get("acceso")
                        datos.acceso.clear()
                        for x in acceso:
                            datos.acceso.add(x)
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
                    reg = Menu.objects.get(pk=codificar(request.POST['id']))
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
                        data['formTitulo'] = 'Crear menu'
                        data['form'] = MenuForms()
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
                        datos = Menu.objects.get(id=codificar(id))
                        data['reg']= id
                        data['form'] = MenuForms(initial={
                                            'nombre': datos.nombre,
                                            'descripcion': datos.descripcion,
                                            'icono': datos.icono,
                                            'ruta': datos.ruta,
                                            'es_principal': datos.es_principal,
                                            'principal': datos.principal,
                                            'acceso': [i.id for i in datos.acceso.all()]
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
                        men = Menu.objects.get(id = codificar(request.GET['id']))
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
                            lista = Menu.objects.filter(Q(nombre__icontains=busqueda) &Q(estado=True))
                        else:
                            lista = Menu.objects.filter(estado=True)
                        data['titulo'] = 'Configuración de menú'
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
                        return render(request, 'vistas/menu.html', data)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})
            else:
                messages.error(request, "No tienes permisos para visualizar esta información")
                return redirect('/')