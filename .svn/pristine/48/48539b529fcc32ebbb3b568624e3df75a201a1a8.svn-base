# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
# from .forms import MenuForms
from .models import Asignatura, Inscripcion
from .funciones import codificar
from django.db.models import Q
from datetime import datetime


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
    data['titulo'] = 'Panel'
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/',"")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""
    data['persona'] = persona = request.session['persona']

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'inscribir':
            try:
                asignatura = Asignatura.objects.get(pk=codificar(request.POST['id']))
                if Inscripcion.objects.filter(persona=persona, asignatura = asignatura).exists():
                    return JsonResponse({"error": True, 'msj': 'Usted ya se encuentra inscrito en esta asignatura'})
                else:
                    inscripcion = Inscripcion(
                        persona=persona,
                        asignatura= asignatura
                    )
                    inscripcion.save(request)
                    messages.success(request, 'Registro Guardado Exitosamente')
                    return JsonResponse({"error": False,'msj':'Se ha inscrito exitosamente'})
            except Exception as ex:
                pass
            return HttpResponseRedirect(ruta)

    else:
        if 'pet' in request.GET:
            pet = request.GET['pet']

            if pet == 'inscribir':
                try:
                    with transaction.atomic():
                        asignatura = Asignatura.objects.get(id=codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": asignatura.nombre})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

        else:
            try:
                with transaction.atomic():
                    busqueda = None
                    if 's' in request.GET:
                        busqueda = request.GET['s']
                    if busqueda:
                        lista = Asignatura.objects.filter(Q(nombre__icontains=busqueda) & Q(estado=True))
                    else:
                        lista = Asignatura.objects.filter(estado=True)
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
                    data['persona'] = persona
                    return render(request, 'vistas/panel.html', data)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})