# Generated by Django 4.0.3 on 2024-06-10 04:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recomendacion', '0004_nivel_alter_ejercicio_nivel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ejercicio',
            name='nivel',
        ),
        migrations.AddField(
            model_name='asignatura',
            name='nivel',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='recomendacion.nivel', verbose_name='Nivel'),
            preserve_default=False,
        ),
    ]
