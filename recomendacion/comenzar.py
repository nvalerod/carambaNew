# -*- coding: UTF-8 -*-
from django.core import signing
from django.core.paginator import Paginator
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import EvaluacionForms
from .models import Asignatura, Inscripcion, Ejercicio, Evaluacion
from .funciones import codificar
from django.db.models import Q
from datetime import datetime
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


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
    data['titulo'] = 'Ejercicios'
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

        elif pet == 'evaluar':
            try:
                with transaction.atomic():
                    form = EvaluacionForms(request.POST)
                    if form.is_valid():
                        evaluacion = Evaluacion(
                            persona=persona,
                            ejercicio = Ejercicio.objects.get(id=codificar(form.cleaned_data['ejercicio'])),
                            duracion = form.cleaned_data['duracion'],
                            gusto = form.cleaned_data['gusto'],
                            dificultad = form.cleaned_data['dificultad'],
                            calificacion = 0,
                            abstraction = 0,
                            paralelismo = 0,
                            pensaminetoLogico = 0,
                            sincronizacion = 0,
                            controFlujo = 0,
                            interactividadUsuario = 0,
                            representacionInformacion = 0,
                        )

                        if 'archivo' in request.FILES:
                            evaluacion.archivo = request.FILES['archivo']
                        else:
                            return JsonResponse({"error": True, 'msj': 'Debe seleccionar un archivo', "to": ruta})

                        evaluacion.save(request)

                        messages.success(request, 'Registro Guardado Exitosamente')
                        return JsonResponse({"error": False, "to": '/'})
                    else:
                        return JsonResponse({"error": True,'msj':'formulario no válido', "to": ruta})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})
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
                    asignatura = codificar(request.GET['id'])
                    data['pet'] = 'evaluar'
                    data['todosEjercicios'] = Ejercicio.objects.filter(asignatura=asignatura)
                    # Obtener todas las evaluaciones relacionadas con la asignatura
                    evaluaciones = Evaluacion.objects.filter(ejercicio__asignatura_id=asignatura).values(
                        'persona_id', 'ejercicio_id', 'gusto', 'dificultad'
                    )
                    df = pd.DataFrame(evaluaciones)

                    # Verificar si el usuario tiene evaluaciones previas
                    user_evaluations = Evaluacion.objects.filter(persona_id=persona.id, ejercicio__asignatura_id=asignatura)

                    if user_evaluations.count() == 0:
                        # Caso de usuario nuevo sin evaluaciones previas
                        # Opción 1: recomendar a resolver el ejercicio más popular (con más evaluaciones)
                        if Evaluacion.objects.filter(ejercicio__asignatura = asignatura).exists():
                            popular_exercises = df.groupby('ejercicio_id').size().sort_values(ascending=False).index[:5].tolist()
                            # se le presenta los 5 mas populares
                            data['ejercicios'] = popular_exercises
                            # de los cuales se le daa resolver el primero de ellos
                            data['resolver'] = ejercicio = Ejercicio.objects.filter(id__in=popular_exercises).first()

                        else:
                            data['ejercicios']= ejercicios = Ejercicio.objects.filter(asignatura=asignatura)
                            data['resolver'] = ejercicio = ejercicios.first()

                        data['form'] = EvaluacionForms(initial={
                            'ejercicio': ejercicio.codificar()
                        })

                        return render(request, 'vistas/comenzar.html', data)
                        # Opción 2: recomendar ejercicios al azar
                        # return Ejercicio.objects.filter(asignatura_id=asignatura_id).order_by('?')[:5]

                    # Pivotar la tabla para crear una matriz persona-ejercicio
                    user_exercise_matrix = df.pivot_table(index='persona_id', columns='ejercicio_id', values=['gusto', 'dificultad'])

                    # Llenar NaN con ceros (o puedes optar por otro valor)
                    user_exercise_matrix = user_exercise_matrix.fillna(0)

                    # Obtener el vector del usuario actual
                    current_user_vector = user_exercise_matrix.loc[persona.id].values.reshape(1, -1)

                    # Calcular similitudes coseno
                    similares = cosine_similarity(current_user_vector, user_exercise_matrix)[0]

                    # Crear un DataFrame con los resultados
                    similarity_df = pd.DataFrame({
                        'persona_id': user_exercise_matrix.index,
                        'similarity': similares
                    })

                    # Excluir al usuario actual
                    similarity_df = similarity_df[similarity_df['persona_id'] != persona.id]

                    # Obtener las 5 personas más similares
                    usuariosSimilares = similarity_df.sort_values(by='similarity', ascending=False).head(5)['persona_id'].tolist()

                    # Obtener los ejercicios que estos usuarios similares han evaluado en esta asignatura, pero que el usuario actual no ha hecho
                    similar_users_evaluations = df[df['persona_id'].isin(usuariosSimilares)]
                    current_user_evaluations = df[df['persona_id'] == persona.id]['ejercicio_id'].tolist()
                    ejerciciosRecomendados = similar_users_evaluations[
                        ~similar_users_evaluations['ejercicio_id'].isin(current_user_evaluations)]['ejercicio_id'].unique()

                    # de existir se le presenta los 5 mas recomendados
                    data['ejercicios'] = recomendaciones =  Ejercicio.objects.filter(id__in=ejerciciosRecomendados)
                    # se consulta si existen ejercicios a recomendar
                    if recomendaciones.exists():
                        #se sugiere resolver el primero de los 5 recomendados
                        data['resolver'] = recomendado = recomendaciones.first()
                        data['form'] = EvaluacionForms(initial={
                            'ejercicio': recomendado.codificar()
                            })
                    else:
                        popular_exercises = df.groupby('ejercicio_id').size().sort_values(ascending=False).index[:5].tolist()
                        data['ejercicios'] = popular_exercises
                        data['resolver'] = popular = Ejercicio.objects.filter(id__in=popular_exercises).order_by('?').first()
                        data['form'] = EvaluacionForms(initial={
                            'ejercicio': popular.codificar()
                            })

                    return render(request, 'vistas/comenzar.html', data)
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"error": True, "msj": str(ex), "to": ruta})