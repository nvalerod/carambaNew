# -*- coding: UTF-8 -*-
from django.core import signing
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .funciones import codificar, generar_usuario,generar_username
from datetime import datetime
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import views as auth_views, authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


from django.core.paginator import Paginator
from .models import Menu, Group, Persona, Sitio
from .forms import CambiarClaveForms, RegistroForms


from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template import Context


# def index_view(request):
#     data = {}
#     data['sitio'] = Sitio.objects.filter(estado=True).last()
#     data['categoria'] = Categoria.objects.filter(estado=True, activo=True)
#     data['redes'] = Redsocial.objects.filter(estado=True, activo=True)
#     data['anuncios'] = Publicidad.objects.filter(estado=True, activo=True, externo = True)
#     data['ventajas'] = Ventaja.objects.filter(estado=True, activo=True)
#     # data['departamento'] = Departamento.objects.filter(estado=True, interno=False, activo=True)
#
#     return render(request,'index.html',data)


class LoginView(auth_views.LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            data={}

            user = authenticate(username=request.POST['username'],
                                password=request.POST['password'])

            data['error'] = True
            if user is not None:
                if user.is_active:
                    login(request, user)
                    data['error'] = False
                    data['user'] = user.username

                    if Sitio.objects.filter(estado=True).exists():
                        request.session['sitio'] = Sitio.objects.filter(estado=True).last()
                    if Persona.objects.filter(usuario=request.user).exists():
                        request.session['persona'] = Persona.objects.get(usuario=request.user)

                    permisos = Group.objects.filter(user=request.user)

                    if request.user.is_superuser:
                        request.session['menu'] = menu = Menu.objects.filter(estado=True, activo=True).order_by('nombre')
                        request.session['menuP'] = menup = Menu.objects.filter(estado=True, activo=True).order_by('nombre')
                    else:
                        request.session['menu'] = menu = Menu.objects.filter(estado=True, acceso__in=permisos,activo=True).order_by('nombre')
                        request.session['menuP'] = menup = Menu.objects.filter(estado=True, es_principal=True,menu__in=menu, activo=True).order_by('principal').distinct('principal')
                else:
                    data['msj'] = 'Usuario no Activo'
            else:
                data['msj'] = 'Usuario Incorrecto'

            return JsonResponse(data)
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sitio'] = Sitio.objects.filter(estado=True).last()
        return context


class LogoutView(LoginRequiredMixin,auth_views.LogoutView):
    pass


class Error404View(TemplateView):
    template_name = 'error_404.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sitio'] = Sitio.objects.filter(estado=True).last()
        return context


class Error500View(TemplateView):
    template_name = 'error_500.html'

    @classmethod
    def as_error_view(cls):
        v = cls.as_view()

        def view(request):
            r = v(request)
            r.render()
            return r

        return view

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sitio'] = Sitio.objects.filter(estado=True).last()
        return context

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "reset/password_reset_email.html"
                    c = {
                    "email":user.email,
                    'domain':'borisan.nas-code.com',
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="reset_password.html", context={"password_reset_form":password_reset_form})
    # return render(request=request, template_name="reset/password_reset.html", context={"password_reset_form":password_reset_form})


@transaction.atomic()
@login_required(redirect_field_name='res',login_url='/login')
def cambiarclave(request):
    global ex
    data = {}
    # model = Menu
    # nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    # data['agregar'] = agregar = request.user.has_perm('{}.add_{}'.format(nombre_app, nombre_model))
    # data['editar'] = editar = request.user.has_perm('{}.change_{}'.format(nombre_app, nombre_model))
    # data['eliminar'] = eliminar = request.user.has_perm('{}.delete_{}'.format(nombre_app, nombre_model))
    # data['ver'] = ver = request.user.has_perm('{}.view_{}'.format(nombre_app, nombre_model))
    data['ruta'] = ruta = request.path
    data['titulo'] = 'Cambiar contraseña'
    data['modulo'] = ruta
    data['migas'] = str(ruta).replace('/',"")
    data['accion'] = request.GET['pet'] if 'pet' in request.GET else ""

    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'cambiar':
            try:
                with transaction.atomic():
                    form = CambiarClaveForms(request.POST)
                    if form.is_valid():
                        usuario = User.objects.get(id=request.user.id)
                        if form.cleaned_data['contraseña1'] == form.cleaned_data['contraseña2']:
                            usuario.set_password(request.POST['contraseña1'])
                            usuario.save()
                            update_session_auth_hash(request, usuario)  # Important!
                            messages.success(request, 'Su contraseña ha sido actualizada')
                            return JsonResponse({"error": False, "to": ruta, 'msj': 'Su contraseña ha sido actualizada'})
                        else:
                            return JsonResponse({"error": True, "to": ruta, 'msj': 'Las contraseñas no coinciden'})
                    else:
                        for error in list(form.errors.values()):
                            messages.error(request, error)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "to": ruta,'msj':'Algo ha salido mal'})

    else:
        try:
            data['formTitulo'] = 'Cambiar contraseña'
            data['form'] = CambiarClaveForms()
            data['pet'] = 'cambiar'
            return render(request, 'formsbase.html', data)
        except Exception as ex:
            pass
        return HttpResponseRedirect(ruta)


@transaction.atomic()
def registrar(request):
    global ex
    data = {}
    data['ruta'] = ruta = request.path
    data['titulo'] = 'Registro'
    if request.method == 'POST':
        pet = request.POST['pet']
        if pet == 'registrar':
            try:
                with transaction.atomic():
                    form = RegistroForms(request.POST)
                    if form.is_valid():
                        if User.objects.filter(username=form.cleaned_data['usuario']).exists():
                            return JsonResponse({"error": True, "to": ruta, 'msj': 'Nombre de usuario ya existe'})

                        user = User.objects.create_user(form.cleaned_data['usuario'], '', form.cleaned_data['contraseña'])
                        user.save()

                        persona = Persona(
                            nombres=form.cleaned_data['nombres'],
                            apellidos=form.cleaned_data['apellidos'],
                            sexo=form.cleaned_data['sexo'],
                            fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                            usuario= user
                        )

                        if 'foto' in request.FILES:
                            persona.foto = request.FILES['foto']

                        persona.save(request)

                        # username = generar_username(persona)
                        # generar_usuario(persona, username)

                        user = User.objects.get(pk=persona.usuario.pk)
                        user.first_name = persona.nombres
                        user.last_name = persona.apellidos
                        user.email = persona.correo
                        user.save()
                        #perfil estudiante 3
                        grupo = Group.objects.get(pk=3)
                        grupo.user_set.add(persona.usuario)
                        grupo.save()

                        login(request, user)
                        request.session['persona'] = Persona.objects.get(usuario=request.user)
                        permisos = Group.objects.filter(user=request.user)
                        request.session['menu'] = menu = Menu.objects.filter(estado=True, acceso__in=permisos,activo=True).order_by('nombre')
                        request.session['menuP'] = menup = Menu.objects.filter(estado=True, es_principal=True,menu__in=menu, activo=True).order_by('principal').distinct('principal')

                        return JsonResponse({"error": False, "to": '/login', 'msj': 'Registro guardado exitosamente'})

                    else:
                        return JsonResponse({"error": True, 'msj': 'formulario no válido', "to": ruta})

            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})

    else:
        try:
            data['formTitulo'] = 'Registro'
            data['form'] = RegistroForms()
            data['pet'] = 'registrar'
            return render(request, 'registrarme.html', data)
        except Exception as ex:
            pass
        return HttpResponseRedirect(ruta)