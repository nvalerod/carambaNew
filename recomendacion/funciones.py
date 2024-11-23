# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from django.core import signing
from django.db.models.functions import math
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from io import BytesIO # nos ayuda a convertir un html en pdf
import smtplib
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render

def codificar(valor):
    if valor.isnumeric():
        result = signing.dumps(valor)
    else:
        result = signing.loads(valor)
    return result

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def generar_usuario(persona, usuario):
    password = '12345'
    anio = ''
    if persona.fecha_nacimiento:
        anio = "*" + str(persona.fecha_nacimiento)[0:4]
        password = persona.cedula.strip()+anio
    user = User.objects.create_user(usuario, '', password)
    user.save()
    persona.usuario = user
    persona.save()


def generar_username(persona):
    inicial=persona.nombres.split(' ')[0][0].lower()
    apellido=persona.apellidos.split(' ')[0].lower()
    usuario=inicial+apellido
    if User.objects.filter(username=usuario).exists():
        cant = User.objects.filter(username=usuario).count()
        usuario = usuario + str(cant)
    return usuario


def generar_nombre_archivo(nombre, original):
    ext = ""
    if original.find(".") > 0:
        ext = original[original.rfind("."):]
    fecha = datetime.now().date()
    hora = datetime.now().time()
    return nombre + fecha.year.__str__() + fecha.month.__str__() + fecha.day.__str__() + hora.hour.__str__() + hora.minute.__str__() + hora.second.__str__() + ext.lower()


def get_verbose_name(app_label, model):
    from django.apps import apps
    try:
        return apps.get_model(app_label, model)._meta.verbose_name
    except LookupError:
        return None

def enviar_correo(request, server,data_correo= {}, template_name ='',data_templete={}):
    msg = MIMEMultipart()
    template= render(request,template_name,data_templete)
    html = template.content.decode('UTF-8')
    msg['From'] =server.user
    msg['To'] = data_correo['To']
    msg['Subject'] = data_correo['Subject']
    msg.attach(MIMEText(html,'html'))
    server.sendmail(msg['From'],msg['To'],msg.as_string())
    server.quit()

def log_correo():
    #Libreria smtplib
    #Instancia smtplib.SMTP('smtp.gmail.com: 587') Nos Inicializar el protocolo de smtp para envio de correo a través del puerto 587
    server = smtplib.SMTP('smtp.gmail.com: 587')
    # Se inicializa el servicio  para envio de correo
    server.starttls()
    #se establece la cuenta de correo que esta EMAIL_HOST_USER  y contraseña  EMAIL_HOST_PASSWORD
    #esta el setting EMAIL_HOST_USER,  EMAIL_HOST_PASSWORD
    server.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
    #se retorna la servicio con la cuenta logeada para poder enviar correos
    return server