# Generated by Django 4.0.3 on 2024-06-10 01:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recomendacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asignatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.BooleanField(default=True)),
                ('nombre', models.CharField(default='', max_length=140, verbose_name='Nombre')),
                ('descripcion', models.TextField(verbose_name='Descripcion')),
                ('foto', models.FileField(blank=True, null=True, upload_to='asignatura/%Y/%m/%d')),
                ('usuario_creacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario_modificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Asignatura',
                'verbose_name_plural': 'Asignaturas',
                'permissions': (('exportar_asignatura', 'puede exportar asignatura'),),
            },
        ),
        migrations.CreateModel(
            name='Contenido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.BooleanField(default=True)),
                ('nombre', models.CharField(default='', max_length=140, verbose_name='Nombre')),
                ('descripcion', models.TextField(verbose_name='Descripcion')),
                ('asignatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recomendacion.asignatura', verbose_name='Asignatura')),
                ('usuario_creacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario_modificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contenido',
                'verbose_name_plural': 'Contenidos',
                'permissions': (('exportar_contenido', 'puede exportar contenido'),),
            },
        ),
        migrations.CreateModel(
            name='Ejercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.BooleanField(default=True)),
                ('nombre', models.CharField(default='', max_length=140, verbose_name='Nombre')),
                ('descripcion', models.TextField(verbose_name='Descripcion')),
                ('dificultad', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)], verbose_name='Dificultad')),
                ('nivel', models.CharField(blank=True, choices=[('1', 'Escuela'), ('2', 'Colegios'), ('3', 'Universidad')], default='1', max_length=1, null=True)),
                ('contenido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recomendacion.contenido', verbose_name='Contenido')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recomendacion.persona', verbose_name='Persona')),
                ('usuario_creacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario_modificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ejercicio',
                'verbose_name_plural': 'Ejercicios',
                'permissions': (('exportar_ejercicio', 'puede exportar ejercicio'),),
            },
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.BooleanField(default=True)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='scratch/%Y/%m/%d')),
                ('duracion', models.CharField(max_length=10)),
                ('gusto', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)])),
                ('dificultad', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)])),
                ('calificacion', models.IntegerField(default=0)),
                ('abstraction', models.IntegerField(default=0)),
                ('paralelismo', models.IntegerField(default=0)),
                ('pensaminetoLogico', models.IntegerField(default=0)),
                ('sincronizacion', models.IntegerField(default=0)),
                ('controFlujo', models.IntegerField(default=0)),
                ('interactividadUsuario', models.IntegerField(default=0)),
                ('representacionInformacion', models.IntegerField(default=0)),
                ('ejercicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recomendacion.ejercicio', verbose_name='Ejercicio')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recomendacion.persona', verbose_name='Persona')),
                ('usuario_creacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario_modificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Evaluacion',
                'verbose_name_plural': 'Evaluaciones',
                'permissions': (('exportar_evaluacion', 'puede exportar evaluacion'),),
            },
        ),
    ]
