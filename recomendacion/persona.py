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

from .forms import PersonaForms
from .models import Persona#, Administrador, Cliente
from .funciones import codificar, generar_usuario, generar_username
from datetime import datetime
from django.db.models import Q

@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def view(request):
    global ex
    data = {}
    model = Persona
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
                    form = PersonaForms(request.POST)
                    if form.is_valid():
                        correo = Persona.objects.filter(estado=True, correo = form.cleaned_data['correo'])
                        if correo.exists():
                            return JsonResponse({"error": True, "to": ruta, 'msj': 'Correo ya se encuentra registrado'})
                        cedula = Persona.objects.filter(estado=True, cedula = form.cleaned_data['cedula'])
                        if cedula.exists():
                            return JsonResponse({"error": True, "to": ruta, 'msj': 'Persona ya existe'})
                        persona = Persona(
                                razonSocial = form.cleaned_data['razonSocial'],
                                nombres = form.cleaned_data['nombres'],
                                apellidos = form.cleaned_data['apellidos'],
                                sexo = form.cleaned_data['sexo'],
                                cedula = form.cleaned_data['cedula'],
                                fecha_nacimiento = form.cleaned_data['fecha_nacimiento'],
                                correo = form.cleaned_data['correo'],
                        )

                        if 'foto' in request.FILES:
                            persona.foto = request.FILES['foto']

                        persona.save(request)

                        username = generar_username(persona)
                        generar_usuario(persona, username)

                        user = User.objects.get(pk=persona.usuario.pk)
                        user.first_name = persona.nombres
                        user.last_name = persona.apellidos
                        user.email = persona.correo
                        user.save()

                        return JsonResponse({"error": False, "to": ruta,'msj':'Registro guardado exitosamente'})
                    else:
                         return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'agregarperfil':
            try:
                with transaction.atomic():
                    empleado = Persona.objects.get(pk=int(request.POST['emplea']))
                    if not User.objects.filter(groups__pk=int(request.POST['perfil']),id=empleado.usuario.pk).exists():
                        grupo = Group.objects.get(pk=int(request.POST['perfil']))
                        grupo.user_set.add(empleado.usuario)
                        grupo.save()
                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": ruta})
                    else:
                        return JsonResponse({"error": True, "to": ruta,'msj':'Perfil ya existe'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'editar':
            try:
                form = PersonaForms(request.POST)
                with transaction.atomic():
                    if form.is_valid():
                        datos = Persona.objects.get(pk=codificar(request.POST['id']))
                        correo = Persona.objects.filter(estado=True, correo=form.cleaned_data['correo']).exclude(id=datos.id)
                        if correo.exists():
                            return JsonResponse({"error": True, "to": ruta, 'msj': 'Correo ya se encuentra registrado'})
                        cedula = Persona.objects.filter(estado=True, cedula=form.cleaned_data['cedula']).exclude(id=datos.id)
                        if cedula.exists():
                            return JsonResponse({"error": True, "to": ruta, 'msj': 'Persona ya existe'})
                        datos.razonSocial = form.cleaned_data['razonSocial']
                        datos.nombres = form.cleaned_data['nombres']
                        datos.apellidos = form.cleaned_data['apellidos']
                        datos.sexo = form.cleaned_data['sexo']
                        datos.cedula = form.cleaned_data['cedula']
                        datos.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                        datos.correo = form.cleaned_data['correo']

                        if 'foto' in request.FILES:
                            datos.foto = request.FILES['foto']

                        datos.save(request)

                        user = User.objects.get(pk=datos.usuario.pk)
                        user.first_name = datos.nombres
                        user.last_name = datos.apellidos
                        user.email = datos.correo
                        user.save()
                        return JsonResponse({"error": False, "to": ruta, 'msj':'Registro guardado exitosamente'})
                    else:
                        return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

        elif pet == 'eliminar':
            if eliminar:
                try:
                    reg = Persona.objects.get(pk=codificar(request.POST['id']))
                    reg.estado = False
                    reg.save(request)
                    return JsonResponse({"error": False})
                except Exception as ex:
                    pass
                return HttpResponseRedirect(ruta)
            else:
                messages.error(request, "No tienes permisos para adicionar")
                return redirect('/persona/')

        elif pet == 'eliminargrupo':
            if eliminar:
                try:
                    empleado = Persona.objects.get(pk=request.POST['idgrupo'])
                    grupo = Group.objects.get(pk=request.POST['id'])
                    grupo.user_set.remove(empleado.usuario)
                    grupo.save()
                    return JsonResponse({"error": False})
                except Exception as ex:
                    pass
                return HttpResponseRedirect(ruta)
            else:
                messages.error(request, "No tienes permisos para adicionar")
                return redirect('/persona/')

        elif pet == 'crearadmin':
            try:
                with transaction.atomic():
                    per = Persona.objects.get(pk=codificar(request.POST['id']))
                    if not Administrador.objects.filter(persona=per, estado=True).exists():
                        admin = Administrador(persona=per,fechaingreso=datetime.now().date(),activo=True)
                        admin.save(request)
                        grupo = Group.objects.get(pk=1)
                        grupo.user_set.add(admin.persona.usuario)
                        grupo.save()
                        return JsonResponse({"error": False, "to": ruta, 'msj': 'Registro guardado correctamente'})
                    else:
                        return JsonResponse({"error": True, "to": ruta,"msj":'Registro ya fue creado'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})

        elif pet == 'crearcliente':
            try:
                with transaction.atomic():
                    per = Persona.objects.get(pk=codificar(request.POST['id']))
                    if not Cliente.objects.filter(persona=per, estado=True).exists():
                        cliente = Cliente(persona=per,fechaingreso=datetime.now().date(),activo=True)
                        cliente.save(request)

                        grupo = Group.objects.get(pk=2)
                        grupo.user_set.add(cliente.persona.usuario)
                        grupo.save()

                        return JsonResponse({"error": False, "to": ruta, 'msj': 'Registro guardado correctamente'})
                    else:
                        return JsonResponse({"error": True, "to": ruta,"msj":'Registro ya fue creado'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta})

        elif pet == 'CambiarEstado':
            try:
                reg = Persona.objects.get(pk=codificar(request.POST['id']))
                usuario = User.objects.get(pk = reg.usuario.pk)
                if usuario.is_active:
                    usuario.is_active = False
                else:
                    usuario.is_active = True
                usuario.save()
                return JsonResponse({"error": False,'msj':'Registro guardado exitosamente'})
            except Exception as ex:
                pass
            return HttpResponseRedirect(ruta)

    else:
        if 'pet' in request.GET:
            pet = request.GET['pet']
            if pet == 'crear':
                if agregar:
                    try:
                        data['formTitulo'] = 'Crear Persona'
                        data['form'] = PersonaForms()
                        data['pet'] = 'crear'
                        return render(request,'formsbase.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/persona/')

            elif pet == 'editar':
                if editar:
                    try:
                        data['formTitulo'] = 'Editar Persona'
                        data['pet'] = 'editar'
                        id = request.GET['id']
                        datos = Persona.objects.get(id=codificar(id))
                        data['reg']= id
                        data['form'] = PersonaForms(initial={
                                            'razonSocial': datos.razonSocial,
                                            'nombres': datos.nombres,
                                            'apellidos': datos.apellidos,
                                            'sexo': datos.sexo,
                                            'cedula': datos.cedula,
                                            'fecha_nacimiento': datos.fecha_nacimiento,
                                            'correo': datos.correo,
                                            'foto': datos.foto,
                                        })
                        return render(request,'formsbase.html',data)
                    except Exception as ex:
                        pass
                    return HttpResponseRedirect(ruta)
                else:
                    messages.error(request, "No tienes permisos para adicionar")
                    return redirect('/persona/')

            elif pet == 'agregargrupo':
                try:
                    titulo = "Agregar Perfil"
                    data['perfil'] = Group.objects.all()
                    template = get_template("vistas/agregargrupopersona.html")
                    json_content = template.render((data))
                    return JsonResponse({"error": False, 'data': json_content, 'titulo': titulo})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "mensaje": "Error al consultar los datos."})

            elif pet == 'eliminar':
                try:
                    with transaction.atomic():
                        empleado = Persona.objects.get(id = codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": empleado.nombres})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet == 'eliminargrupo':
                try:
                    with transaction.atomic():

                        # empleado = User.objects.get(groups__id=request.GET['id'])

                        empleado = Group.objects.get(pk=request.GET['id'])
                        return JsonResponse({"error": False, "dato": empleado.name})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet == 'crearadmin':
                try:
                    with transaction.atomic():
                        persona = Persona.objects.get(id=codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": persona.nombres +" "+persona.apellidos})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet == 'crearcliente':
                try:
                    with transaction.atomic():
                        persona = Persona.objects.get(id=codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": persona.nombres +" "+persona.apellidos})
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})

            elif pet == 'CambiarEstado':
                try:
                    with transaction.atomic():
                        persona = Persona.objects.get(id = codificar(request.GET['id']))
                        return JsonResponse({"error": False, "dato": persona.nombres})
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
                            lista = Persona.objects.filter((Q(nombres__icontains=busqueda ) | Q(cedula__icontains=busqueda ) | Q(apellidos__icontains=busqueda ))& Q(estado=True))
                        else:
                            lista = Persona.objects.filter(estado=True)
                        perfil = User.objects.all()
                        data['titulo'] = 'Persona'
                        paginator = Paginator(lista, 6)
                        page_number = request.GET.get('page') or 1
                        obj_pag = paginator.get_page(page_number)
                        pag_act = signing.dumps(int(page_number))
                        paginas = range(1, obj_pag.paginator.num_pages + 1)
                        data['obj_pag'] = obj_pag
                        grupo = []
                        for x in perfil:
                            p = x.groups.all()
                            for j in p:
                                datos = {'pk': x.pk, 'grupo': j.name,'idgrupo': j.id}
                                grupo.append(datos)
                        data['grupo'] = grupo
                        data['lista'] = obj_pag
                        data['pag_act'] = pag_act
                        data['paginas'] = paginas
                        data['busqueda'] = busqueda if busqueda else ""
                        return render(request, 'vistas/persona.html', data)
                except Exception as ex:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": True, "to": ruta})
            else:
                messages.error(request, "No tienes permisos para visualizar esta información")
                return redirect('/')