# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import EjercicioForms
from .models import Ejercicio
from .funciones import codificar
from django.db.models import Q


@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    model = Ejercicio
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
    data['persona'] = persona = request.session['persona']

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'crear':
            try:
                with transaction.atomic():
                    form = EjercicioForms(request.POST)
                    if form.is_valid():
                        ejercicio = Ejercicio(
                                persona = persona,
                                asignatura = form.cleaned_data['asignatura'],
                                # contenido = form.cleaned_data['contenido'],
                                nombre = form.cleaned_data['nombre'],
                                descripcion = form.cleaned_data['descripcion'],
                                dificultad = form.cleaned_data['dificultad'],

                        )
                        ejercicio.save(request)

                        contenido = form.cleaned_data.get("contenido")
                        for x in contenido:
                            ejercicio.contenido.add(x)

                        # ejercicio.save(request)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                         return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'editar':
            try:
                form = EjercicioForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Ejercicio.objects.get(pk=codificar(request.POST['id']))
                        datos.asignatura = form.cleaned_data['asignatura']
                        # datos.contenido = form.cleaned_data['contenido']
                        datos.nombre = form.cleaned_data['nombre']
                        datos.descripcion = form.cleaned_data['descripcion']
                        datos.dificultad = form.cleaned_data['dificultad']

                        contenido = form.cleaned_data.get("contenido")
                        datos.contenido.clear()
                        for x in contenido:
                            datos.contenido.add(x)

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
                    reg = Ejercicio.objects.get(pk=codificar(request.POST['id']))
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
                        data['formTitulo'] = 'Crear ejercicio'
                        data['form'] = EjercicioForms()
                        data['pet'] = 'crear'
                        return render(request,'formsbase.html',data)
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
                        datos = Ejercicio.objects.get(id=codificar(id))
                        data['reg']= id
                        data['form'] = EjercicioForms(initial={
                                            'asignatura': datos.asignatura,
                                            'contenido': [i.id for i in datos.contenido.all()],
                                            'nombre': datos.nombre,
                                            'descripcion': datos.descripcion,
                                            'dificultad': datos.dificultad,

                                        })
                        return render(request,'formsbase.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'eliminar':
                try:
                    with transaction.atomic():
                        men = Ejercicio.objects.get(id = codificar(request.GET['id']))
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
                            lista = Ejercicio.objects.filter(Q(nombre__icontains=busqueda) &Q(estado=True))
                        else:
                            lista = Ejercicio.objects.filter(estado=True)
                        data['titulo'] = 'Ejercicios'
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
                        return render(request, 'vistas/ejercicios.html', data)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

            else:
                messages.error(request, "No tienes permisos para visualizar esta información")
                return redirect('/')