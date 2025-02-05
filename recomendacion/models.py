# coding=utf-8
from django.db import models
from django.contrib.auth.models import User, Group
from django.core import signing
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import Permission
from django.http import request
from datetime import datetime
from django.db.models import Sum
from django.core.validators import MaxValueValidator, MinValueValidator

class BaseModel(models.Model):
    usuario_creacion = models.ForeignKey(User, related_name='+', blank=True, null=True,on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_modificacion = models.ForeignKey(User, related_name='+', blank=True, null=True,on_delete=models.PROTECT)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        usuario = None
        if len(args):
            usuario = args[0].user.id
        if self.id:
            self.usuario_modificacion_id = usuario
        else:
            self.usuario_creacion_id = usuario
        models.Model.save(self)

    class Meta:
        abstract = True

    def codificar(self):
        result = signing.dumps(self.pk)
        return result


tipo_sexo = (
            (1, 'MASCULINO'),
            (2, 'FEMENINO')
)


class Persona(BaseModel):
    cedula=models.CharField(default='',max_length=10, verbose_name='Cedula')
    nombres = models.CharField(default='',max_length=140, verbose_name='Nombre')
    apellidos = models.CharField(default='', max_length=60, verbose_name="Apellido")
    correo = models.EmailField(default='', max_length=140, verbose_name="Correo")
    sexo = models.IntegerField(choices=tipo_sexo, default=1, null=True, blank=True,verbose_name="Sexo")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    foto = models.FileField(upload_to='foto/%Y/%m/%d', null=True, blank=True)

    class Meta:
        permissions = (
            ('exportar_persona', 'puede exportar persona'),
        )
        ordering = ['apellidos',]
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return '%s %s' % (self.apellidos, self.nombres)

    def save(self, *args, **kwargs):
        self.nombres=self.nombres.title().strip()
        self.apellidos = self.apellidos.title().strip()
        super(Persona, self).save(*args, **kwargs)

    def edad(self):
        hoy = datetime.now().today()
        nacimiento = self.fecha_nacimiento
        # return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (hoy.month, nacimiento.day))
        return hoy.year - nacimiento.year

    def nombrecompleto(self):
        return self.nombres + ' ' + self.apellidos

class Menu(BaseModel):
    nombre = models.CharField(default='', max_length=140, verbose_name='Titulo')
    descripcion = models.CharField(default='', null=True, blank=True, max_length=140, verbose_name='Descripcion')
    icono = models.ImageField(verbose_name="icono", blank=True, null=True, upload_to='icono/')
    ruta = models.CharField(default='', max_length=140, verbose_name='Ruta')
    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    principal = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    acceso = models.ManyToManyField(Group, verbose_name='acceso')

    class Meta:
        permissions = (
            ('exportar_menu', 'puede exportar menu'),
        )
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return '{}'.format(self.nombre)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip()
        self.descripcion = self.descripcion.strip()
        super(Menu, self).save(*args, **kwargs)

    def modulo(self):
        return Menu.objects.filter(principal = self, estado =True)

    def tiene_submenu(self):
        return Menu.objects.filter(principal=self, estado=True).exists()

class MenuPerfil(BaseModel):
    menu = models.ForeignKey(Menu, verbose_name='Menu', on_delete=models.CASCADE)
    perfil = models.ManyToManyField(Group, verbose_name='Perfil')

    class Meta:
        permissions = (
            ('exportar_menuperfil', 'puede exportar menu perfil'),
        )
        verbose_name = "Menu Perfil"
        verbose_name_plural = "Menu Perfiles"

    def __str__(self):
        return '{}'.format(self.menu.nombre)

class Sitio(BaseModel):
    nombresitio = models.CharField(default='', max_length=140, verbose_name='NombreSitio')
    icono = models.ImageField(verbose_name="icono", blank=True, null=True, upload_to='icono/')
    favicono = models.ImageField(verbose_name="favicono", blank=True, null=True, upload_to='favicono/')
    correo = models.EmailField(default='', max_length=140, verbose_name='correo')
    clave = models.CharField(default='', max_length=140, verbose_name='clave')

    class Meta:
        permissions = (
            ('exportar_sitio', 'puede exportar sitio'),
        )
        verbose_name = 'Sitio'
        verbose_name_plural = 'Sitios'

    def __str__(self):
        return '{}'.format(self.nombresitio)

    def save(self, *args, **kwargs):
        self.nombresitio = self.nombresitio.strip()
        super(Sitio, self).save(*args, **kwargs)

class Nivel(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.CharField(default='', max_length=140, verbose_name='Descripcion')

    class Meta:
        permissions = (
            ('exportar_nivel', 'puede exportar nivel'),
        )
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'

    def __str__(self):
        return '{}'.format(self.descripcion)

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.strip()
        super(Nivel, self).save(*args, **kwargs)

class Asignatura(BaseModel):
    nombre = models.CharField(default='', max_length=140, verbose_name='Nombre')
    descripcion = models.TextField( verbose_name='Descripcion')
    nivel = models.ForeignKey(Nivel, verbose_name='Nivel', on_delete=models.CASCADE)
    imagen = models.FileField(upload_to='asignatura/%Y/%m/%d', null=True, blank=True)

    class Meta:
        permissions = (
            ('exportar_asignatura', 'puede exportar asignatura'),
        )
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'

    def __str__(self):
        return '{}'.format(self.nombre)

    def inscrito(self, persona):

        return Inscripcion.objects.filter(asignatura = self, persona = persona).exists()

    def matriculado(self):

        return Inscripcion.objects.filter(asignatura = self).count()

    def ejercicio(self):

        return Ejercicio.objects.filter(asignatura = self).count()

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip()
        super(Asignatura, self).save(*args, **kwargs)


class Contenido(BaseModel):
    asignatura = models.ForeignKey(Asignatura, verbose_name='Asignatura', on_delete=models.CASCADE)
    nombre = models.CharField(default='', max_length=140, verbose_name='Nombre')
    descripcion = models.TextField( verbose_name='Descripcion')

    class Meta:
        permissions = (
            ('exportar_contenido', 'puede exportar contenido'),
        )
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'

    def __str__(self):
        return '{}'.format(self.nombre)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip()
        super(Contenido, self).save(*args, **kwargs)

class Ejercicio(BaseModel):
    persona = models.ForeignKey(Persona, verbose_name='Persona', on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, verbose_name='Asignatura', on_delete=models.CASCADE)
    contenido = models.ManyToManyField(Contenido, verbose_name='Contenido')
    nombre = models.CharField(default='', max_length=140, verbose_name='Nombre')
    descripcion = models.TextField( verbose_name='Descripcion')
    dificultad = models.IntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(0)],verbose_name='Dificultad' )

    class Meta:
        permissions = (
            ('exportar_ejercicio', 'puede exportar ejercicio'),
        )
        verbose_name = 'Ejercicio'
        verbose_name_plural = 'Ejercicios'

    def __str__(self):
        return '{}'.format(self.nombre)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.strip()
        super(Ejercicio, self).save(*args, **kwargs)


class Evaluacion(BaseModel):
    persona = models.ForeignKey(Persona, verbose_name='Persona', on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, verbose_name='Ejercicio', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='scratch/%Y/%m/%d', null=True, blank=True)
    duracion = models.CharField(max_length=10)
    gusto = models.IntegerField(default=0, validators=[MaxValueValidator(6), MinValueValidator(0)])
    dificultad = models.IntegerField(default=0, validators=[MaxValueValidator(6), MinValueValidator(0)])
    calificacion = models.IntegerField(default=0)
    abstraction = models.IntegerField(default=0)
    paralelismo = models.IntegerField(default=0)
    pensaminetoLogico = models.IntegerField(default=0)
    sincronizacion = models.IntegerField(default=0)
    controFlujo = models.IntegerField(default=0)
    interactividadUsuario = models.IntegerField(default=0)
    representacionInformacion = models.IntegerField(default=0)


    class Meta:
        permissions = (
            ('exportar_evaluacion', 'puede exportar evaluacion'),
        )
        verbose_name = 'Evaluacion'
        verbose_name_plural = 'Evaluaciones'

    def __str__(self):
        return '%s - %s' % (self.persona.nombrecompleto(), self.ejercicio.nombre)


class Inscripcion(BaseModel):
    persona = models.ForeignKey(Persona, verbose_name='Persona', on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, verbose_name='Asignatura', on_delete=models.CASCADE)
    fechaInscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('exportar_inscripcion', 'puede exportar inscripcion'),
        )
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'

    def __str__(self):
        return '{}'.format(self.persona.nombrecompleto())