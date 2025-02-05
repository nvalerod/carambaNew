# Generated by Django 4.0.3 on 2024-06-10 04:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recomendacion', '0003_rename_evaluation_evaluacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nivel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.BooleanField(default=True)),
                ('descripcion', models.CharField(default='', max_length=140, verbose_name='Descripcion')),
                ('usuario_creacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('usuario_modificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contenido',
                'verbose_name_plural': 'Contenidos',
                'permissions': (('exportar_nivel', 'puede exportar nivel'),),
            },
        ),
        migrations.AlterField(
            model_name='ejercicio',
            name='nivel',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='recomendacion.nivel', verbose_name='Nivel'),
            preserve_default=False,
        ),
    ]
