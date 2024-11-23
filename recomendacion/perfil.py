# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .forms import PerfilForms
from .models import Group, Permission, Menu
from .funciones import codificar, render_to_pdf, get_verbose_name
from xlwt import *
from xlwt import easyxf
from django.db.models import Q



@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    model = Group
    nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    data['agregar'] = agregar = request.user.has_perm('{}.add_{}'.format(nombre_app, nombre_model))
    data['editar'] = editar = request.user.has_perm('{}.change_{}'.format(nombre_app, nombre_model))
    data['eliminar'] = eliminar = request.user.has_perm('{}.delete_{}'.format(nombre_app, nombre_model))
    data['ver'] = ver = request.user.has_perm('{}.view_{}'.format(nombre_app, nombre_model))
    data['ruta'] = ruta = request.path
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/', "")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'crear':
            try:
                with transaction.atomic():
                    form = PerfilForms(request.POST)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                         raise NameError('Error')
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})

        elif pet == 'editar':
            try:
                with transaction.atomic():
                    group = Group.objects.get(pk=int(request.POST['id']))
                    form = PerfilForms(request.POST, instance=group)
                    form.save()
                    messages.success(request, 'Registro Guardado Exitosamente')
                    return JsonResponse({"error": False, "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})

        elif pet == 'eliminar':
            if eliminar:
                try:
                    reg = Group.objects.get(pk=request.POST['id'])
                    reg.delete()
                    return JsonResponse({"error": False})
                except Exception as ex:
                    pass
                return HttpResponseRedirect(ruta)
            else:
                messages.error(request, "No tienes permisos para adicionar")
                return redirect('/')

        elif pet == 'actpermi':
            try:
                with transaction.atomic():
                    perfil = Group.objects.get(pk=request.POST['rol'])
                    seleccion  = request.POST['select']
                    perm = Permission.objects.get(codename=request.POST['perm'])
                    if seleccion == 'true':
                        perm.group_set.add(perfil)
                        perm.save()
                    else:
                        perm.group_set.remove(perfil)
                        perm.save()

                    return JsonResponse({"error": False})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})

        elif pet == 'actacceso':
            try:
                with transaction.atomic():
                    perfil = Group.objects.get(pk=request.POST['rol'])
                    seleccion  = request.POST['select']
                    menu = Menu.objects.get(pk= codificar(request.POST['men']))
                    if seleccion == 'true':
                        perfil.menu_set.add(menu)
                        perfil.save()
                    else:
                        perfil.menu_set.remove(menu)
                        perfil.save()

                    return JsonResponse({"error": False})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})

    else:
        if 'pet' in request.GET:
            pet = request.GET['pet']
            if pet == 'crear':
                if agregar:
                    try:
                        data['formTitulo'] = 'Crear Perfil'
                        data['form'] = form = PerfilForms()
                        form.fields["permissions"].queryset = Permission.objects.exclude(
                            content_type__model__in=['session', 'user', 'permission', 'contenttype', 'logentry','configuracion']).order_by('name')
                        data['pet'] = 'crear'
                        return render(request, 'formsbase.html', data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'editar':
                if editar:
                    try:
                        data['formTitulo'] = 'Editar Perfil'
                        data['pet'] = 'editar'
                        id = int(request.GET['id'])
                        group = Group.objects.get(pk=id)
                        data['reg']= id
                        data["form"] = form = PerfilForms(instance=group)
                        permisos = []
                        ch_perms = list(group.permissions.all().values_list('id', flat=True))
                        qs_permisos = form.fields["permissions"].queryset
                        for p in qs_permisos.values('content_type__model', 'content_type__app_label',
                                                    'content_type__id').order_by('content_type__model').distinct():
                            # permisos.append({"modelo": p["content_type__model"].title(),
                            #                  "permisos": qs_permisos.filter(content_type_id=p["content_type__id"])})
                            nombreModelo = get_verbose_name(p["content_type__app_label"], p['content_type__model'])
                            nombreModelo = nombreModelo.title() if nombreModelo else p['content_type__model'].title()
                            permisos.append({"modelo": nombreModelo,
                                             "permisos": qs_permisos.filter(content_type_id=p["content_type__id"])})
                        permisos = list(sorted(permisos, key=lambda i: i['modelo']))
                        data["permisos"] = permisos
                        data["ch_perms"] = ch_perms
                        return render(request, 'formsbase.html', data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/')

            elif pet == 'eliminar':
                try:
                    with transaction.atomic():
                        perf = Group.objects.get(id = request.GET['id'])
                        return JsonResponse({"error": False, "dato": perf.name})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet == 'consulpermi':
                try:
                    with transaction.atomic():
                        perf = Menu.objects.filter(estado=True, acceso__pk=request.GET['id'])
                        permisos = Group.objects.get(pk=request.GET['id'])

                        json_permisos = []
                        for x in permisos.permissions.all():
                            json_permisos.append({
                                'perm': x.codename,
                            })

                        json = []
                        for p in perf:
                            json.append({
                                'id':p.pk,
                            })
                        return JsonResponse({"error": False, "dato": json,"perm":json_permisos})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet == 'pdf':
                try:
                    data['perfiles'] = Group.objects.all()
                    return render_to_pdf(
                        'reportes/repperfiles.html',
                        {
                            'pagesize': 'A4',
                            'data': data,
                        }
                    )
                except Exception as ex:
                    pass

            elif pet == 'excel':
                try:
                    __author__ = 'vinculacion'
                    title = easyxf('font: name Times New Roman, color-index black, bold on , height 350; alignment: horiz centre')
                    font_style = XFStyle()
                    font_style.font.bold = True
                    font_style2 = XFStyle()
                    font_style2.font.bold = False
                    wb = Workbook(encoding='utf-8')
                    ws = wb.add_sheet('perfiles')
                    ws.write_merge(0, 0, 0, 5, 'DIRECCIÓN DE VINCULACIÓN', title)
                    nombre = "PERFILES.xls"
                    response = HttpResponse(content_type="application/ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=' + nombre
                    columns = [
                        (u"No.", 2000),
                        (u"PERFIL", 5000),
                    ]
                    row_num = 3
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num][0], font_style)
                        ws.col(col_num).width = columns[col_num][1]
                    row_num = 4
                    i = 0
                    for perfil in Group.objects.all():
                        i += 1
                        ws.write(row_num, 0, i, font_style2)
                        ws.write(row_num, 1, perfil.name, font_style2)
                        row_num += 1
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass
        else:
            if ver:
                busqueda = None
                if 's' in request.GET:
                    busqueda = request.GET['s']
                if busqueda:
                    lista = Group.objects.filter(name__icontains=busqueda)
                else:
                    lista = Group.objects.all().order_by('name')

                data['titulo'] = 'Roles y permisos'

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
                data['permisos'] = permisos = Permission.objects.exclude(content_type__model__in=['session', 'user', 'permission', 'contenttype', 'logentry', 'configuracion']).order_by('name')
                modelos = []
                accesos = []
                for p in permisos.values('content_type__model').order_by('content_type__model').distinct():
                    modelos.append({'name': p['content_type__model'].replace("group", "Perfil"),})

                for p in permisos.values('name','codename','content_type__app_label','content_type__model'):
                    accesos.append({
                            'name': p['content_type__model'].replace("group", "Perfil"),
                            'codename': p['codename'],
                            'content_type__app_label': p['content_type__app_label'],
                            # 'content_type__model': ' '.join(str(p['name']).lower().replace("can", "Puede") \
                            #                                       .replace('add', 'Agregar') \
                            #                                       .replace('view', 'Ver') \
                            #                                       .replace('delete', 'Eliminar') \
                            #                                       .replace('change', 'Modificar').split(' ')[0:2])
                    })


                data['modelos'] = modelos
                data['accesos'] = accesos
                data['menus'] = Menu.objects.filter(estado=True)
                return render(request, 'vistas/perfil.html', data)
            else:
                messages.error(request, "No tienes permisos para visualizar esta información")
                return redirect('/')
