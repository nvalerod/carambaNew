# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import AsignaturaForms, ContenidoForms
from .models import Asignatura, Contenido
from .funciones import codificar
from django.db.models import Q


@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    model = Asignatura
    nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    data['agregar'] = agregar = request.user.has_perm('{}.add_{}'.format(nombre_app, nombre_model))
    data['editar'] = editar = request.user.has_perm('{}.change_{}'.format(nombre_app, nombre_model))
    data['eliminar'] = eliminar = request.user.has_perm('{}.delete_{}'.format(nombre_app, nombre_model))
    data['ver'] = ver = request.user.has_perm('{}.view_{}'.format(nombre_app, nombre_model))
    data['ruta'] = ruta = request.path
    data['titulo'] = 'Asignatura'
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/',"")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'crear':
            try:
                with transaction.atomic():
                    form = AsignaturaForms(request.POST)
                    if form.is_valid():
                        asignatura = Asignatura(
                                nombre = form.cleaned_data['nombre'],
                                descripcion = form.cleaned_data['descripcion'],
                                nivel = form.cleaned_data['nivel'],
                        )

                        if 'imagen' in request.FILES:
                            asignatura.imagen = request.FILES['imagen']

                        asignatura.save(request)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                         return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'editar':
            try:
                form = AsignaturaForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Asignatura.objects.get(pk=codificar(request.POST['id']))
                        datos.nombre = form.cleaned_data['nombre']
                        datos.descripcion = form.cleaned_data['descripcion']
                        if 'imagen' in request.FILES:
                            datos.imagen = request.FILES['imagen']

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
                    reg = Asignatura.objects.get(pk=codificar(request.POST['id']))
                    reg.estado = False
                    reg.save(request)
                    return JsonResponse({"error": False})
                except Exception as ex:
                    pass
                return HttpResponseRedirect(ruta)
            else:
                messages.error(request, "No tienes permisos para adicionar")
                return redirect('/')

        elif pet == 'crearContenido':
            try:
                with transaction.atomic():
                    form = ContenidoForms(request.POST)
                    if form.is_valid():
                        contenido = Contenido(
                                asignatura=Asignatura.objects.get(id=codificar(request.GET['id'])),
                                nombre = form.cleaned_data['nombre'],
                                descripcion = form.cleaned_data['descripcion'],
                        )
                        contenido.save(request)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                         return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'editarContenido':
            try:
                form = ContenidoForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Contenido.objects.get(pk=codificar(request.POST['id']))
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

        elif pet == 'eliminarContenido':
            if eliminar:
                try:
                    reg = Contenido.objects.get(pk=codificar(request.POST['id']))
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
                        data['formTitulo'] = 'Crear asignatura'
                        data['form'] = AsignaturaForms()
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
                        datos = Asignatura.objects.get(id=codificar(id))
                        data['reg']= id
                        data['form'] = AsignaturaForms(initial={
                                        'nombre': datos.nombre,
                                        'descripcion': datos.descripcion,
                                        'nivel': datos.nivel,
                                        'imagen': datos.imagen,
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
                        men = Asignatura.objects.get(id = codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": men.descripcion})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet =='verContenido':
                if ver:
                    try:
                        with transaction.atomic():
                            busqueda = None

                            if 's' in request.GET:
                                busqueda = request.GET['s']
                            if busqueda:
                                lista = Contenido.objects.filter(Q(asignatura = codificar(request.GET['id'])) & Q(nombre__icontains=busqueda) & Q(estado=True))
                            else:
                                lista = Contenido.objects.filter(asignatura = codificar(request.GET['id']), estado =True)
                            data['titulo'] = 'Contenido'
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
                            data['id'] = request.GET['id']
                            return render(request, 'vistas/contenido.html', data)
                    except Exception as ex:
                        transaction.set_rollback(True)
                        return JsonResponse({"error": True, "to": ruta})
                else:
                    messages.error(request, "No tienes permisos para visualizar esta información")
                    return redirect('/')

            elif pet == 'crearContenido':
                if agregar:
                    try:
                        data['formTitulo'] = 'Crear contenido'
                        data['form'] = ContenidoForms()
                        data['pet'] = 'crearContenido'
                        data['reg'] = request.GET['id']
                        return render(request,'formsbase.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'editarContenido':
                if editar:
                    try:
                        data['formTitulo'] = 'Editar contenido'
                        data['pet'] = 'editarContenido'
                        id = request.GET['id']
                        datos = Contenido.objects.get(id=codificar(id))
                        data['reg']= id
                        data['form'] = ContenidoForms(initial={
                                        'nombre': datos.nombre,
                                        'descripcion': datos.descripcion,
                                        })
                        return render(request,'formsbase.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'eliminarContenido':
                try:
                    with transaction.atomic():
                        men = Contenido.objects.get(id = codificar(request.GET['id']))
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
                            lista = Asignatura.objects.filter(Q(nombre__icontains=busqueda) &Q(estado=True))
                        else:
                            lista = Asignatura.objects.filter(estado=True)
                        data['titulo'] = 'Asignatura'
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
                        return render(request, 'vistas/asignatura.html', data)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})
            else:
                messages.error(request, "No tienes permisos para visualizar esta información")
                return redirect('/')