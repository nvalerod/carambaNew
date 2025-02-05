from django.urls import re_path, include, path
import recomendacion.login as seguridad
from django.contrib.auth import views as auth_views
from recomendacion import login, panel, sitio, menu, perfil, persona, asignatura, nivel, ejercicios, comenzar, miperfil

urlpatterns = [
    re_path(r'^login/$', login.LoginView.as_view(), name='login'),
    path(route='logout/', view=seguridad.LogoutView.as_view(), name='logout'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset/password_reset_complete.html'), name='password_reset_complete'),


    re_path(r'^$',panel.view, name='panel'),
    re_path(r'^sitio/$', sitio.view, name='sitio'),
    re_path(r'^menu/$', menu.view, name='menu'),
    re_path(r'^perfiles/$', perfil.view, name='perfil'),
    re_path(r'^persona/$', persona.view, name='persona'),
    re_path(r'^nivel/$', nivel.view, name='nivel'),
    re_path(r'^asignatura/$', asignatura.view, name='asignatura'),
    re_path(r'^ejercicio/$', ejercicios.view, name='ejercicios'),
    re_path(r'^comenzar/$', comenzar.view, name='comenzar'),
    re_path(r'^registrarme/$', login.registrar, name='registrarme'),
    re_path(r'^miperfil/$', miperfil.view, name='miperfil'),

    path("restablecer_clave", login.password_reset_request, name="restablecerclave"),
]
