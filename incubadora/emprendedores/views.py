from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .forms import SesionMentoriaForm, ArchivoSesionForm, PropuestaHorarioForm, ResponderSesionForm, MinutaSesionForm, RegistroUsuarioProyectoForm, TutorRegistrationForm, MensajeForm, ProyectoForm, ConvocatoriaForm, CategoriaForm, DocumentoPlantillaForm, BancoProblemaForm
import json
from datetime import timedelta
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from .models import Mensaje, SesionMentoria, ArchivoSesion, EventoSesion, PropuestaHorario, Proyecto, Tutor, Tarea, EmprendedorProfile, Convocatoria, Categoria, DocumentoPlantilla, ParticipanteForum, ConfiguracionCorreo, BancoProblema
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MiembroComision, Comision
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ProgramaForum
from .models import ParticipanteForum
from .forms import ParticipanteForumForm
from .forms import PropuestaHorarioForm
from .models import EventoSesion
from .models import SesionMentoria
from .models import Mensaje
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# Vista de inicio
def inicio(request):
    return render(request, 'emprendedores/inicio.html')

# Vista de registro de proyecto
def registro_proyecto(request):
    return render(request, 'emprendedores/registro.html')

# Vista de éxito de registro
def registro_exito(request):
    return render(request, 'emprendedores/registro_exito.html')

# Vista de detalle de proyecto
def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    return render(request, 'emprendedores/detalle_proyecto.html', {'proyecto': proyecto})

# Vista para cambiar estado de proyecto
def cambiar_estado_proyecto(request, proyecto_id, nuevo_estado):
    return redirect('detalle_proyecto', proyecto_id=proyecto_id)

# Vista de registro de usuario
def registro_usuario(request, tipo_usuario):
    if tipo_usuario != 'emprendedor':
        messages.error(request, "Tipo de usuario no válido.")
        return redirect('inicio')
    
    if request.method == 'POST':
        form = RegistroUsuarioProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear el usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['nombre_completo'].split()[0],
                last_name=' '.join(form.cleaned_data['nombre_completo'].split()[1:]),
            )
            
            # Crear el proyecto
            proyecto = Proyecto.objects.create(
                usuario=user,
                nombre_proyecto=form.cleaned_data['nombre_proyecto'],
                descripcion=form.cleaned_data['descripcion'],
                nombre_completo=form.cleaned_data['nombre_completo'],
                email=form.cleaned_data['email'],
                telefono=form.cleaned_data['telefono'],
                sector=form.cleaned_data['sector'],
                archivo_proyecto=form.cleaned_data['archivo_proyecto'],
                presupuesto_estimado=form.cleaned_data.get('presupuesto_estimado'),
            )
            
            # Crear perfil de emprendedor
            EmprendedorProfile.objects.create(user=user)
            
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, "¡Registro exitoso! Tu proyecto ha sido enviado para revisión.")
            return redirect('panel_emprendedor')
    else:
        form = RegistroUsuarioProyectoForm()
    
    return render(request, 'emprendedores/registro_usuario.html', {
        'form': form,
        'tipo_usuario': tipo_usuario
    })

# Vista de login
def login_view(request):
    from django.contrib.auth import authenticate
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.first_name}!")
            
            if user.is_superuser:
                return redirect('panel_admin')
            elif hasattr(user, 'tutor'):
                return redirect('panel_tutor')
            else:
                return redirect('panel_emprendedor')
        else:
            messages.error(request, "Credenciales inválidas. Por favor, inténtalo de nuevo.")
    
    return render(request, 'emprendedores/login.html')

# Vista de logout
def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')

# Vista de panel de usuario
def panel_usuario(request):
    if request.user.is_superuser:
        return redirect('panel_admin')
    elif hasattr(request.user, 'tutor'):
        return redirect('panel_tutor')
    else:
        return redirect('panel_emprendedor')

def panel_admin(request):
    # Obtener parámetros de búsqueda y filtros
    search_query = request.GET.get('search', '')
    tutor_especialidad_filter = request.GET.get('tutor_especialidad', '')
    emprendedor_tutor_filter = request.GET.get('emprendedor_tutor', '')
    proyecto_estado_filter = request.GET.get('proyecto_estado', '')

    # Filtrar tutores
    tutores = Tutor.objects.all()
    if search_query:
        tutores = tutores.filter(
            Q(usuario__first_name__icontains=search_query) |
            Q(usuario__last_name__icontains=search_query) |
            Q(usuario__username__icontains=search_query)
        )
    if tutor_especialidad_filter:
        tutores = tutores.filter(especialidades__icontains=tutor_especialidad_filter)

    # Filtrar emprendedores
    tutor_user_ids = Tutor.objects.values_list('usuario_id', flat=True)
    emprendedores = User.objects.filter(is_superuser=False).exclude(id__in=tutor_user_ids)
    if search_query:
        emprendedores = emprendedores.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    if emprendedor_tutor_filter:
        emprendedores = emprendedores.filter(emprendedor_profile__tutor_id=emprendedor_tutor_filter)

    # Filtrar proyectos
    proyectos = Proyecto.objects.all()
    if proyecto_estado_filter:
        proyectos = proyectos.filter(estado=proyecto_estado_filter)

    # Para cada emprendedor, calcular el número de proyectos
    for emprendedor in emprendedores:
        emprendedor.num_proyectos = Proyecto.objects.filter(usuario=emprendedor).count()
        if not hasattr(emprendedor, 'emprendedor_profile'):
            EmprendedorProfile.objects.create(user=emprendedor)
    
    # Obtener lista de tutores para el filtro de emprendedores
    todos_tutores = Tutor.objects.all()

    # Obtener choices de estados de proyecto
    estados_proyecto = Proyecto.ESTADOS

    # Manejar envío de mensajes
    if request.method == 'POST' and 'enviar_mensaje' in request.POST:
        form = MensajeForm(request.POST)
        if form.is_valid():
            try:
                destinatario = User.objects.get(id=form.cleaned_data['destinatario_id'])
                mensaje = Mensaje(
                    remitente=request.user,
                    destinatario=destinatario,
                    tipo_destinatario=form.cleaned_data['tipo_destinatario'],
                    asunto=form.cleaned_data['asunto'],
                    contenido=form.cleaned_data['contenido']
                )
                mensaje.save()
                messages.success(request, "Mensaje enviado correctamente.")
            except User.DoesNotExist:
                messages.error(request, "El destinatario no existe.")
        else:
            messages.error(request, "Error al enviar el mensaje. Por favor, verifica los datos.")

    return render(request, 'emprendedores/admin.html', {
        'tutores': tutores,
        'emprendedores': emprendedores,
        'proyectos': proyectos,
        'todos_tutores': todos_tutores,
        'estados_proyecto': estados_proyecto,
        'search_query': search_query,
        'tutor_especialidad_filter': tutor_especialidad_filter,
        'emprendedor_tutor_filter': emprendedor_tutor_filter,
        'proyecto_estado_filter': proyecto_estado_filter,
    })

# Vista de panel de tutor
@login_required
def panel_tutor(request):
    if not hasattr(request.user, 'tutor'):
        return redirect('panel_usuario')
    
    tutor = get_object_or_404(Tutor, usuario=request.user)
    # Obtener proyectos asignados a este tutor específico
    proyectos = Proyecto.objects.filter(tutor=tutor)
    hoy = timezone.now()
    
    sesiones_pendientes = SesionMentoria.objects.filter(
        proyecto__in=proyectos,
        estado__in=['propuesta', 'pendiente_confirmacion', 'reprogramacion_solicitada']
    ).order_by('fecha_propuesta')[:5]
    
    sesiones_proximas = SesionMentoria.objects.filter(
        proyecto__in=proyectos,
        estado__in=['confirmada', 'propuesta'],
        fecha_propuesta__gte=hoy
    ).order_by('fecha_propuesta')[:5]
    
    sesiones_requieren_atencion = SesionMentoria.objects.filter(
        proyecto__in=proyectos,
        estado='confirmada',
        fecha_propuesta__range=(hoy, hoy + timedelta(days=2)),
        es_material_obligatorio=True
    ).exclude(archivos__isnull=False).distinct()

    # Solicitudes de sesión enviadas por emprendedores (propuesta, no creada por el tutor)
    solicitudes_sesion = SesionMentoria.objects.filter(
        proyecto__in=proyectos,
        estado='propuesta',
    ).exclude(creada_por=request.user).order_by('fecha_propuesta')
    
    # Calcular métricas reales
    tareas_pendientes = Tarea.objects.filter(
        proyecto__in=proyectos,
        completada=False,
        fecha_limite__gte=timezone.now()
    ).order_by('fecha_limite')[:10]

    tareas_completadas_lista = Tarea.objects.filter(
        proyecto__in=proyectos,
        completada=True
    ).order_by('-fecha_limite')[:10]

    tareas_completadas = Tarea.objects.filter(
        proyecto__in=proyectos,
        completada=True
    ).count()

    tareas_total = Tarea.objects.filter(
        proyecto__in=proyectos
    ).count()
    
    # Calcular horas totales de sesiones realizadas
    from django.db.models import Sum
    horas_totales = SesionMentoria.objects.filter(
        proyecto__in=proyectos, estado='realizada'
    ).aggregate(total=Sum('duracion'))['total'] or 0
    horas_totales = horas_totales // 60  # Convertir minutos a horas
    
    # Calcular progreso promedio
    if proyectos.exists():
        progreso_promedio = sum([p.progreso for p in proyectos]) / proyectos.count()
    else:
        progreso_promedio = 0
    
    # Preparar eventos para el calendario
    eventos_calendario = []
    for sesion in SesionMentoria.objects.filter(proyecto__in=proyectos, estado='confirmada'):
        eventos_calendario.append({
            'title': f"Sesión: {sesion.proyecto.nombre_proyecto}",
            'start': sesion.fecha_propuesta.isoformat(),
            'end': (sesion.fecha_propuesta + timedelta(minutes=sesion.duracion)).isoformat(),
            'url': reverse('detalle_sesion', args=[sesion.id])
        })
    
    return render(request, 'emprendedores/tutor.html', {
        'proyectos': proyectos,
        'tutor': tutor,
        'sesiones_pendientes': sesiones_pendientes,
        'sesiones_proximas': sesiones_proximas,
        'sesiones_requieren_atencion': sesiones_requieren_atencion,
        'tareas_pendientes': tareas_pendientes,
        'tareas_completadas': tareas_completadas,
        'tareas_completadas_lista': tareas_completadas_lista,
        'tareas_total': tareas_total,
        'horas_totales': horas_totales,
        'progreso_promedio': progreso_promedio,
        'promedio_evaluaciones': 0,
        'eventos_calendario': eventos_calendario,
        'solicitudes_sesion': solicitudes_sesion,
    })

# Vista de panel de emprendedor
@login_required
def panel_emprendedor(request):
    proyectos = Proyecto.objects.filter(usuario=request.user)
    return render(request, 'emprendedores/paneles/emprendedor.html', {'proyectos': proyectos})

# Vista para asignar tutor a proyecto
def asignar_tutor(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.method == 'POST':
        tutor_id = request.POST.get('tutor_id')
        if tutor_id:
            tutor = get_object_or_404(Tutor, id=tutor_id)
            
            # Verificar si el tutor tiene disponibilidad
            if tutor.proyectos_actuales >= tutor.max_proyectos:
                messages.error(request, f"El tutor {tutor.usuario.get_full_name()} ya tiene el máximo de proyectos asignados ({tutor.max_proyectos}).")
                return redirect('asignar_tutor', proyecto_id=proyecto_id)
            
            # Asignar el tutor al proyecto
            proyecto.tutor = tutor
            proyecto.estado = 'asignado'
            proyecto.save()
            
            messages.success(request, f"Tutor {tutor.usuario.get_full_name()} asignado exitosamente al proyecto {proyecto.nombre_proyecto}.")
            return redirect('panel_admin')
    
    # Obtener tutores disponibles
    tutores_disponibles = Tutor.objects.all()
    
    return render(request, 'emprendedores/asignar_tutor.html', {
        'proyecto': proyecto,
        'tutores': tutores_disponibles
    })

# Vista para registrar tutor
def registrar_tutor(request):
    if request.method == 'POST':
        form = TutorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                tutor = form.save()
                messages.success(request, f"Tutor {tutor.usuario.get_full_name()} registrado exitosamente.")
                return redirect('panel_admin')
            except Exception as e:
                messages.error(request, f"Error al registrar tutor: {str(e)}")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = TutorRegistrationForm()
    
    return render(request, 'emprendedores/registrar_tutor.html', {'form': form})

# Vista para eliminar tutor
def eliminar_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    usuario = tutor.usuario
    
    if request.method == 'POST':
        tutor.delete()
        usuario.delete()
        messages.success(request, f"Tutor {usuario.get_full_name()} eliminado exitosamente.")
        return redirect('panel_admin')
    
    return render(request, 'emprendedores/eliminar_tutor.html', {'tutor': tutor})

# Vista para editar tutor
def editar_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    
    if request.method == 'POST':
        form = TutorRegistrationForm(request.POST, instance=tutor)
        
        if form.isvalid():
            try:
                tutor_actualizado = form.save()
                messages.success(request, f"Tutor {tutor_actualizado.usuario.get_full_name()} actualizado exitosamente.")
                return redirect('panel_admin')
            except Exception as e:
                messages.error(request, f"Error al actualizar tutor: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TutorRegistrationForm(instance=tutor, initial={
            'username': tutor.usuario.username,
            'nombre_completo': tutor.usuario.get_full_name(),
            'telefono': tutor.telefono,
            'cedula': tutor.cedula,
            'grado_academico': tutor.grado_academico,
            'institucion': tutor.institucion,
            'especialidades': tutor.especialidades,
            'experiencia': tutor.experiencia,
            'areas_tutorizar': tutor.areas_tutorizar,
            'max_proyectos': tutor.max_proyectos,
        })
    
    return render(request, 'emprendedores/editar_tutor.html', {'form': form, 'tutor': tutor})

def ver_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    return render(request, 'emprendedores/ver_tutor.html', {'tutor': tutor})

# Vista para ver información del emprendedor
def ver_emprendedor(request, emprendedor_id):
    emprendedor = get_object_or_404(User, id=emprendedor_id)
    proyectos = Proyecto.objects.filter(usuario=emprendedor)
    
    if not hasattr(emprendedor, 'emprendedor_profile'):
        EmprendedorProfile.objects.create(user=emprendedor)
    
    return render(request, 'emprendedores/ver_emprendedor.html', {
        'emprendedor': emprendedor,
        'proyectos': proyectos
    })

# Vista para asignar tutor a emprendedor
def asignar_tutor_emprendedor(request, emprendedor_id):
    emprendedor = get_object_or_404(User, id=emprendedor_id)
    profile, created = EmprendedorProfile.objects.get_or_create(user=emprendedor)
    
    if request.method == 'POST':
        tutor_id = request.POST.get('tutor_id')
        
        if tutor_id:
            tutor = get_object_or_404(Tutor, id=tutor_id)
            
            if tutor.proyectos_actuales >= tutor.max_proyectos:
                messages.error(request, f"El tutor {tutor.usuario.get_full_name()} ya tiene el máximo de proyectos asignados ({tutor.max_proyectos}).")
                return redirect('asignar_tutor_emprendedor', emprendedor_id=emprendedor_id)
            
            profile.tutor = tutor
            profile.save()
            
            messages.success(request, f"El tutor {tutor.usuario.get_full_name()} fue asignado al emprendedor {emprendedor.get_full_name()}.")
            return redirect('panel_admin')
    
    todos_tutores = Tutor.objects.all()
    tutores_disponibles = [tutor for tutor in todos_tutores if tutor.proyectos_actuales < tutor.max_proyectos]
    
    return render(request, 'emprendedores/asignar_tutor_emprendedor.html', {
        'emprendedor': emprendedor,
        'tutores': tutores_disponibles,
        'tutor_actual': profile.tutor
    })

@login_required
@require_POST
def completar_tarea_ajax(request, tarea_id):
    try:
        tarea = get_object_or_404(Tarea, id=tarea_id)
        tarea.completada = not tarea.completada
        tarea.save()
        return JsonResponse({'status': 'success', 'completada': tarea.completada})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
        
# Vista para enviar mensaje
@login_required
def enviar_mensaje(request):
    if request.method == 'POST':
        destinatario_id = request.POST.get('destinatario_id')
        tipo_destinatario = request.POST.get('tipo_destinatario')
        asunto = request.POST.get('asunto', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        archivo = request.FILES.get('archivo')

        if destinatario_id and asunto and contenido:
            try:
                destinatario = User.objects.get(id=destinatario_id)
                mensaje = Mensaje.objects.create(
                    remitente=request.user,
                    destinatario=destinatario,
                    tipo_destinatario=tipo_destinatario or 'emprendedor',
                    asunto=asunto,
                    contenido=contenido,
                    archivo=archivo,
                )
                messages.success(request, 'Mensaje enviado correctamente.')
            except User.DoesNotExist:
                messages.error(request, 'El destinatario no existe.')
            except Exception as e:
                messages.error(request, f'Error al enviar el mensaje: {str(e)}')
        else:
            messages.error(request, 'El asunto y el contenido son obligatorios.')

    # Redirigir según el tipo de usuario
    if request.user.is_superuser:
        return redirect('panel_admin')
    elif hasattr(request.user, 'tutor'):
        return redirect('bandeja_tutor')
    else:
        return redirect('panel_emprendedor')

# Vista para agendar evento
def agendar_evento(request):
    return JsonResponse({'status': 'success'})

# Vista para cambiar estado de proyecto (tutor)
@login_required
def cambiar_estado_proyecto_tutor(request, proyecto_id):
    if not hasattr(request.user, 'tutor'):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('panel_tutor')
    
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if proyecto.tutor != request.user.tutor:
        messages.error(request, "No tienes permisos para modificar este proyecto.")
        return redirect('panel_tutor')
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        estados_permitidos = ['pendiente', 'revision', 'asignado', 'finalizado']
        
        if nuevo_estado in estados_permitidos:
            estado_anterior = proyecto.estado
            proyecto.estado = nuevo_estado
            proyecto.save()
            
            # Mensajes por estado para el emprendedor
            mensajes_estado = {
                'pendiente': f'Tu proyecto "{proyecto.nombre_proyecto}" ha sido marcado como Pendiente.',
                'revision': f'Tu proyecto "{proyecto.nombre_proyecto}" ha pasado a revisión. Tu tutor está evaluando el avance.',
                'asignado': f'Tu proyecto "{proyecto.nombre_proyecto}" está En Proceso. Tu tutor ha comenzado el seguimiento activo.',
                'finalizado': f'¡Felicidades! Tu proyecto "{proyecto.nombre_proyecto}" ha sido marcado como Finalizado.',
            }
            
            # Enviar mensaje interno al emprendedor si tiene usuario asignado
            if proyecto.usuario:
                Mensaje.objects.create(
                    remitente=request.user,
                    destinatario=proyecto.usuario,
                    tipo_destinatario='emprendedor',
                    asunto=f'Actualización de estado: {proyecto.nombre_proyecto}',
                    contenido=mensajes_estado.get(nuevo_estado, f'El estado de tu proyecto ha cambiado a {proyecto.get_estado_display()}.'),
                )
            
            # Crear tarea automática según la transición de estado
            fecha_limite_auto = timezone.now() + timedelta(days=7)
            
            tareas_auto = {
                'revision': {
                    'titulo': f'Realizar evaluación inicial del proyecto "{proyecto.nombre_proyecto}"',
                    'descripcion': f'Revisar y evaluar el estado inicial del proyecto "{proyecto.nombre_proyecto}". Documentar observaciones y retroalimentación para el emprendedor.',
                    'prioridad': 'alta',
                },
                'asignado': {
                    'titulo': f'Definir hitos y plan de trabajo con emprendedor de "{proyecto.nombre_proyecto}"',
                    'descripcion': f'Coordinar con el emprendedor del proyecto "{proyecto.nombre_proyecto}" para definir los hitos del proyecto y establecer un plan de trabajo detallado.',
                    'prioridad': 'alta',
                },
                'finalizado': {
                    'titulo': f'Realizar informe de cierre del proyecto "{proyecto.nombre_proyecto}"',
                    'descripcion': f'Elaborar el informe final de cierre del proyecto "{proyecto.nombre_proyecto}" con los resultados obtenidos, lecciones aprendidas y recomendaciones.',
                    'prioridad': 'media',
                },
            }
            
            if nuevo_estado in tareas_auto and nuevo_estado != estado_anterior:
                datos_tarea = tareas_auto[nuevo_estado]
                Tarea.objects.create(
                    titulo=datos_tarea['titulo'],
                    descripcion=datos_tarea['descripcion'],
                    prioridad=datos_tarea['prioridad'],
                    fecha_limite=fecha_limite_auto,
                    completada=False,
                    proyecto=proyecto,
                    asignada_a=request.user,
                )
            
            messages.success(request, f'Estado del proyecto "{proyecto.nombre_proyecto}" actualizado a {proyecto.get_estado_display()}.')
        else:
            messages.error(request, "Estado no válido.")
    
    return redirect('panel_tutor')

# Vista para rechazar proyecto
@login_required
def rechazar_proyecto(request, proyecto_id):
    if not hasattr(request.user, 'tutor'):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('panel_tutor')
    
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Verificar que el proyecto está asignado a este tutor
    if proyecto.tutor != request.user.tutor:
        messages.error(request, "No tienes permisos para rechazar este proyecto.")
        return redirect('panel_tutor')
    
    if request.method == 'POST':
        razon_rechazo = request.POST.get('razon_rechazo')
        if razon_rechazo and len(razon_rechazo) >= 10:
            # Guardar la razón del rechazo en el proyecto
            proyecto.motivo_rechazo = razon_rechazo
            proyecto.estado = 'rechazado'
            proyecto.save()
            
            # Enviar mensaje al administrador
            try:
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    mensaje_admin = Mensaje(
                        remitente=request.user,
                        destinatario=admin_user,
                        tipo_destinatario='administrador',
                        asunto=f"Proyecto Rechazado: {proyecto.nombre_proyecto}",
                        contenido=f"El tutor {request.user.get_full_name()} ha rechazado el proyecto '{proyecto.nombre_proyecto}'.\n\nRazón del rechazo:\n{razon_rechazo}\n\nEmprendedor: {proyecto.nombre_completo}\nEmail: {proyecto.email}"
                    )
                    mensaje_admin.save()
            except Exception as e:
                print(f"Error al enviar mensaje al administrador: {e}")
            
            # Enviar mensaje al emprendedor
            if proyecto.usuario:
                try:
                    mensaje_emprendedor = Mensaje(
                        remitente=request.user,
                        destinatario=proyecto.usuario,
                        tipo_destinatario='emprendedor',
                        asunto=f"Proyecto Rechazado: {proyecto.nombre_proyecto}",
                        contenido=f"Lamentamos informarte que tu proyecto '{proyecto.nombre_proyecto}' ha sido rechazado.\n\nRazón del rechazo:\n{razon_rechazo}\n\nSi tienes preguntas, por favor contacta al administrador del sistema."
                    )
                    mensaje_emprendedor.save()
                except Exception as e:
                    print(f"Error al enviar mensaje al emprendedor: {e}")
            
            messages.success(request, "Proyecto rechazado correctamente. Se han enviado las notificaciones.")
            return redirect('panel_tutor')
        else:
            messages.error(request, "Debe proporcionar una razón detallada de al menos 10 caracteres.")
            return render(request, 'emprendedores/rechazar_proyecto.html', {'proyecto': proyecto})
    
    # Si es una solicitud GET, mostrar el formulario
    return render(request, 'emprendedores/rechazar_proyecto.html', {'proyecto': proyecto})


@login_required
def agregar_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Crear el proyecto asociado al usuario actual
            proyecto = form.save(commit=False)
            proyecto.usuario = request.user
            proyecto.estado = 'pendiente'
            proyecto.save()
            
            messages.success(request, "¡Proyecto registrado exitosamente! Estará pendiente de revisión.")
            return redirect('panel_emprendedor')
    else:
        form = ProyectoForm(user=request.user)
    
    return render(request, 'emprendedores/agregar_proyecto.html', {'form': form})

# Vistas para el Forum Evento 
@login_required
def gestion_convocatoria(request):
    # Solo administradores pueden gestionar convocatorias
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    convocatorias = Convocatoria.objects.all().order_by('-fecha_creacion')
    convocatoria_activa = Convocatoria.objects.filter(activa=True).first()
    
    if request.method == 'POST':
        form = ConvocatoriaForm(request.POST)
        if form.is_valid():
            # Si se marca como activa, desactivar las demás
            if form.cleaned_data['activa']:
                Convocatoria.objects.filter(activa=True).update(activa=False)
            
            form.save()
            messages.success(request, "Convocatoria guardada exitosamente.")
            return redirect('gestion_convocatoria')
    else:
        form = ConvocatoriaForm()
    
    return render(request, 'emprendedores/gestion_convocatoria.html', {
        'form': form,
        'convocatorias': convocatorias,
        'convocatoria_activa': convocatoria_activa
    })

@login_required
def editar_convocatoria(request, convocatoria_id):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
    
    if request.method == 'POST':
        form = ConvocatoriaForm(request.POST, instance=convocatoria)
        if form.is_valid():
            # Si se marca como activa, desactivar las demás
            if form.cleaned_data['activa']:
                Convocatoria.objects.filter(activa=True).exclude(id=convocatoria_id).update(activa=False)
            
            form.save()
            messages.success(request, "Convocatoria actualizada exitosamente.")
            return redirect('gestion_convocatoria')
    else:
        form = ConvocatoriaForm(instance=convocatoria)
    
    return render(request, 'emprendedores/editar_convocatoria.html', {
        'form': form,
        'convocatoria': convocatoria
    })

@login_required
def gestion_categorias(request, convocatoria_id):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.convocatoria = convocatoria
            categoria.save()
            messages.success(request, "Categoría agregada exitosamente.")
            return redirect('gestion_categorias', convocatoria_id=convocatoria_id)
    else:
        form = CategoriaForm()
    
    return render(request, 'emprendedores/gestion_categorias.html', {
        'form': form,
        'convocatoria': convocatoria,
        'categorias': convocatoria.categorias.all()
    })

@login_required
def gestion_documentos(request):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    documentos = DocumentoPlantilla.objects.all()
    
    if request.method == 'POST':
        form = DocumentoPlantillaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento agregado exitosamente.")
            return redirect('gestion_documentos')
    else:
        form = DocumentoPlantillaForm()
    
    return render(request, 'emprendedores/gestion_documentos.html', {
        'form': form,
        'documentos': documentos
    })

def ver_convocatoria(request):
    convocatoria_activa = Convocatoria.objects.filter(activa=True).first()
    documentos = DocumentoPlantilla.objects.all()
    
    return render(request, 'emprendedores/ver_convocatoria.html', {
        'convocatoria': convocatoria_activa,
        'documentos': documentos
    })

# Vista para el forum evento de ciencias técnicas e innovación
def forum_evento(request):
    convocatoria_activa = Convocatoria.objects.filter(activa=True).first()
    return render(request, 'emprendedores/forum_evento.html', {
        'convocatoria': convocatoria_activa
    })


def programa_forum(request):
    return render(request, 'emprendedores/programa_forum.html')

def comite_organizador(request):
    return render(request, 'emprendedores/comite_organizador.html')

def comision_forum(request):
    return render(request, 'emprendedores/comision_forum.html')

def comision_forum(request):
    miembros = MiembroComision.objects.all()
    comisiones = Comision.objects.all()
    return render(request, 'emprendedores/comision_forum.html', {
        'miembros': miembros,
        'comisiones': comisiones
    })

@login_required
def agregar_miembro(request):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        cargo = request.POST.get('cargo')
        preside_comite = True if request.POST.get('preside_comite') == 'on' else False

        MiembroComision.objects.create(
            nombre=nombre,
            apellido=apellido,
            cargo=cargo,
            preside_comite=preside_comite
        )
        messages.success(request, "Miembro agregado correctamente.")
        return redirect('comision_forum')

    return render(request, 'emprendedores/agregar_miembro.html')

@login_required
def editar_miembro(request, miembro_id):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    miembro = get_object_or_404(MiembroComision, id=miembro_id)

    if request.method == 'POST':
        miembro.nombre = request.POST.get('nombre')
        miembro.apellido = request.POST.get('apellido')
        miembro.cargo = request.POST.get('cargo')
        miembro.preside_comite = True if request.POST.get('preside_comite') == 'on' else False
        miembro.save()
        messages.success(request, "Miembro actualizado correctamente.")
        return redirect('comision_forum')

    return render(request, 'emprendedores/editar_miembro.html', {'miembro': miembro})


@login_required
def eliminar_miembro(request, miembro_id):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    miembro = get_object_or_404(MiembroComision, id=miembro_id)
    miembro.delete()
    messages.success(request, "Miembro eliminado correctamente.")
    return redirect('comision_forum')

@login_required
def agregar_comision(request):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        presidente_id = request.POST.get('presidente')
        integrantes_ids = request.POST.getlist('integrantes')

        presidente = get_object_or_404(MiembroComision, id=presidente_id)
        comision = Comision.objects.create(nombre=nombre, presidente=presidente)
        comision.integrantes.set(integrantes_ids)
        messages.success(request, "Comisión agregada correctamente.")
        return redirect('comision_forum')

    miembros = MiembroComision.objects.all()
    return render(request, 'emprendedores/agregar_comision.html', {'miembros': miembros})

@login_required
def editar_comision(request, comision_id):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    comision = get_object_or_404(Comision, id=comision_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        presidente_id = request.POST.get('presidente')
        integrantes_ids = request.POST.getlist('integrantes')

        comision.nombre = nombre
        comision.presidente = get_object_or_404(MiembroComision, id=presidente_id)
        comision.save()
        comision.integrantes.set(integrantes_ids)
        messages.success(request, "Comisión actualizada correctamente.")
        return redirect('comision_forum')

    miembros = MiembroComision.objects.all()
    return render(request, 'emprendedores/editar_comision.html', {'comision': comision, 'miembros': miembros})

@login_required
def eliminar_comision(request, comision_id):
    if not request.user.is_superuser:
        return redirect('forum_evento')
    
    comision = get_object_or_404(Comision, id=comision_id)
    comision.delete()
    messages.success(request, "Comisión eliminada correctamente.")
    return redirect('comision_forum')    

def programa_forum(request):
    programas = ProgramaForum.objects.all().order_by('horario')
    return render(request, 'emprendedores/programa_forum.html', {'programas': programas})

@login_required
def agregar_actividad_programa(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('programa_forum')
    
    if request.method == 'POST':
        horario = request.POST.get('horario')
        actividad = request.POST.get('actividad')
        responsable = request.POST.get('responsable')
        trabajo = request.POST.get('trabajo')
        
        ProgramaForum.objects.create(
            horario=horario,
            actividad=actividad,
            responsable=responsable,
            trabajo=trabajo
        )
        messages.success(request, "Actividad agregada correctamente.")
        return redirect('programa_forum')
    
    return render(request, 'emprendedores/agregar_actividad_programa.html')

@login_required
def editar_actividad_programa(request, actividad_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('programa_forum')
    
    actividad = get_object_or_404(ProgramaForum, id=actividad_id)
    
    if request.method == 'POST':
        actividad.horario = request.POST.get('horario')
        actividad.actividad = request.POST.get('actividad')
        actividad.responsable = request.POST.get('responsable')
        actividad.trabajo = request.POST.get('trabajo')
        actividad.save()
        
        messages.success(request, "Actividad actualizada correctamente.")
        return redirect('programa_forum')
    
    return render(request, 'emprendedores/editar_actividad_programa.html', {'actividad': actividad})

@login_required
def eliminar_actividad_programa(request, actividad_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('programa_forum')
    
    actividad = get_object_or_404(ProgramaForum, id=actividad_id)
    actividad.delete()
    
    messages.success(request, "Actividad eliminada correctamente.")
    return redirect('programa_forum') 


def proyectos_finalizados(request):
    proyectos = Proyecto.objects.filter(estado='finalizado').order_by('-fecha_registro')
    return render(request, 'emprendedores/proyectos_finalizados.html', {'proyectos': proyectos})

def trabajos_innovacion(request):
    trabajos = TrabajoInnovacion.objects.all().order_by('-año')
    return render(request, 'emprendedores/trabajos_innovacion.html', {'trabajos': trabajos})

def agregar_trabajo_innovacion(request):
    if not request.user.is_superuser:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = TrabajoInnovacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trabajo de innovación agregado correctamente.')
            return redirect('trabajos_innovacion')
    else:
        form = TrabajoInnovacionForm()
    
    return render(request, 'emprendedores/agregar_trabajo_innovacion.html', {'form': form})

def editar_trabajo_innovacion(request, trabajo_id):
    if not request.user.is_superuser:
        return redirect('inicio')
    
    trabajo = get_object_or_404(TrabajoInnovacion, id=trabajo_id)
    if request.method == 'POST':
        form = TrabajoInnovacionForm(request.POST, instance=trabajo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trabajo de innovación actualizado correctamente.')
            return redirect('trabajos_innovacion')
    else:
        form = TrabajoInnovacionForm(instance=trabajo)
    
    return render(request, 'emprendedores/editar_trabajo_innovacion.html', {'form': form, 'trabajo': trabajo})

def eliminar_trabajo_innovacion(request, trabajo_id):
    if not request.user.is_superuser:
        return redirect('inicio')
    
    trabajo = get_object_or_404(TrabajoInnovacion, id=trabajo_id)
    trabajo.delete()
    messages.success(request, 'Trabajo de innovación eliminado correctamente.')
    return redirect('trabajos_innovacion')

# Vista para proyectos finalizados
def proyectos_finalizados(request):
    proyectos = Proyecto.objects.filter(estado='finalizado').order_by('-fecha_registro')
    return render(request, 'emprendedores/proyectos_finalizados.html', {'proyectos': proyectos})

# Vista para el resumen de innovación
def resumen_innovacion(request):
    resumenes = ResumenInnovacion.objects.all().order_by('-año', 'categoria')
    return render(request, 'emprendedores/resumen_innovacion.html', {'resumenes': resumenes})

# Vista para agregar entrada al resumen (solo admin)
def agregar_resumen_innovacion(request):
    if not request.user.is_superuser:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = ResumenInnovacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada agregada al resumen correctamente.')
            return redirect('resumen_innovacion')
    else:
        form = ResumenInnovacionForm()
    
    return render(request, 'emprendedores/agregar_resumen_innovacion.html', {'form': form})

# Vista para editar entrada del resumen (solo admin)
def editar_resumen_innovacion(request, resumen_id):
    if not request.user.is_superuser:
        return redirect('inicio')
    
    resumen = get_object_or_404(ResumenInnovacion, id=resumen_id)
    if request.method == 'POST':
        form = ResumenInnovacionForm(request.POST, instance=resumen)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada actualizada correctamente.')
            return redirect('resumen_innovacion')
    else:
        form = ResumenInnovacionForm(instance=resumen)
    
    return render(request, 'emprendedores/editar_resumen_innovacion.html', {'form': form, 'resumen': resumen})

def eliminar_resumen_innovacion(request, resumen_id):
    if not request.user.is_superuser:
        return redirect('inicio')
    
    resumen = get_object_or_404(ResumenInnovacion, id=resumen_id)
    resumen.delete()
    messages.success(request, 'Entrada eliminada correctamente.')
    return redirect('resumen_innovacion')        


def participar_forum(request):
    if request.method == 'POST':
        form = ParticipanteForumForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                participante = form.save()
                
                # Obtener el correo configurado
                configuracion = ConfiguracionCorreo.objects.filter(activo=True).first()
                if configuracion:
                    # Enviar correo con los archivos adjuntos
                    from django.core.mail import EmailMessage
                    email = EmailMessage(
                        f'Nueva inscripción al Forum: {participante.numero_expediente}',
                        f'Se ha recibido una nueva inscripción al Forum de Ciencias Técnicas e Innovación.\n\n'
                        f'Número de expediente: {participante.numero_expediente}\n'
                        f'Nombre: {participante.nombre_completo}\n'
                        f'Carné de identidad: {participante.carne_identidad}\n'
                        f'Centro de trabajo: {participante.centro_trabajo}\n'
                        f'Contacto: {participante.contacto}',
                        settings.DEFAULT_FROM_EMAIL,
                        [configuracion.email],
                    )
                    
                    # Adjuntar archivos
                    archivos = [
                        participante.ponencia,
                        participante.ficha_tecnica,
                        participante.avales,
                        participante.presentacion
                    ]
                    
                    for archivo in archivos:
                        if archivo:
                            email.attach(archivo.name, archivo.read(), archivo.content_type)
                    
                    email.send()
                
                messages.success(request, f'¡Inscripción exitosa! Su número de expediente es: {participante.numero_expediente}')
                return redirect('confirmacion_inscripcion', numero_expediente=participante.numero_expediente)
            except Exception as e:
                messages.error(request, f'Error al procesar la inscripción: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = ParticipanteForumForm()

    return render(request, 'emprendedores/participar_forum.html', {'form': form})

def confirmacion_inscripcion(request, numero_expediente):
    participante = get_object_or_404(ParticipanteForum, numero_expediente=numero_expediente)
    return render(request, 'emprendedores/confirmacion_inscripcion.html', {'participante': participante})

def ver_estado_inscripcion(request):
    numero_expediente = request.GET.get('numero_expediente', '')
    participante = None
    
    if numero_expediente:
        try:
            participante = ParticipanteForum.objects.get(numero_expediente=numero_expediente)
        except ParticipanteForum.DoesNotExist:
            messages.error(request, 'No se encontró ningún expediente con ese número.')
    
    return render(request, 'emprendedores/ver_estado_inscripcion.html', {
        'participante': participante,
        'numero_expediente': numero_expediente
    })

@login_required
def gestionar_correo(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('inicio')
    
    configuraciones = ConfiguracionCorreo.objects.all().order_by('-activo', '-fecha_creacion')
    configuracion_activa = ConfiguracionCorreo.objects.filter(activo=True).first()
    
    if request.method == 'POST':
        from .forms import ConfiguracionCorreoForm
        form = ConfiguracionCorreoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Configuración de correo guardada exitosamente.')
                return redirect('gestionar_correo')
            except Exception as e:
                messages.error(request, f'Error al guardar la configuración: {str(e)}')
    else:
        from .forms import ConfiguracionCorreoForm
        form = ConfiguracionCorreoForm()
    
    return render(request, 'emprendedores/gestionar_correo.html', {
        'form': form,
        'configuraciones': configuraciones,
        'configuracion_activa': configuracion_activa
    })

@login_required
def eliminar_configuracion_correo(request, configuracion_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('inicio')
    
    configuracion = get_object_or_404(ConfiguracionCorreo, id=configuracion_id)
    
    if request.method == 'POST':
        configuracion.delete()
        messages.success(request, 'Configuración de correo eliminada exitosamente.')
    
    return redirect('gestionar_correo')

# Vista para crear sesión de mentoría
@login_required
def crear_sesion_mentoria(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # Verificar que el usuario es tutor y tiene este proyecto asignado
    if not hasattr(request.user, 'tutor') or proyecto.tutor != request.user.tutor:
        messages.error(request, "No tienes permisos para crear sesiones en este proyecto.")
        return redirect('panel_tutor')

    if request.method == 'POST':
        # Leer campos del modal directamente
        objetivo = request.POST.get('objetivo', '').strip()
        tipo = request.POST.get('tipo', '').strip()
        fecha_propuesta = request.POST.get('fecha_propuesta', '').strip()
        duracion = request.POST.get('duracion', '60').strip()
        formato = request.POST.get('formato', 'virtual').strip()
        agenda = request.POST.get('agenda', '').strip()
        materiales_requeridos = request.POST.get('materiales_requeridos', '').strip()

        # Validaciones básicas
        if not objetivo or not tipo or not fecha_propuesta:
            messages.error(request, "El objetivo, tipo y fecha son obligatorios.")
            return redirect('panel_tutor')

        try:
            sesion = SesionMentoria.objects.create(
                proyecto=proyecto,
                creada_por=request.user,
                objetivo=objetivo,
                tipo=tipo,
                fecha_propuesta=fecha_propuesta,
                duracion=int(duracion),
                formato=formato,
                agenda=agenda,
                materiales_requeridos=materiales_requeridos,
                estado='propuesta',
            )

            # Registrar evento
            EventoSesion.objects.create(
                sesion=sesion,
                usuario=request.user,
                accion='crear_sesion',
                detalles=f"Sesión '{objetivo}' creada. Tipo: {tipo}. Formato: {formato}."
            )

            # Notificar al emprendedor si tiene usuario
            if proyecto.usuario:
                Mensaje.objects.create(
                    remitente=request.user,
                    destinatario=proyecto.usuario,
                    tipo_destinatario='emprendedor',
                    asunto=f'Nueva sesión agendada: {objetivo}',
                    contenido=(
                        f'Tu tutor ha agendado una sesión de mentoría para el proyecto "{proyecto.nombre_proyecto}".\n\n'
                        f'Objetivo: {objetivo}\nFecha: {fecha_propuesta}\nDuración: {duracion} minutos\nModalidad: {formato}'
                    ),
                )

            messages.success(request, f'Sesión "{objetivo}" agendada correctamente.')

        except Exception as e:
            messages.error(request, f'Error al crear la sesión: {str(e)}')

        return redirect('panel_tutor')

    # GET: mostrar formulario clásico (por si se accede por URL directa)
    form = SesionMentoriaForm(proyecto=proyecto, usuario=request.user)
    return render(request, 'emprendedores/sesiones/crear_sesion.html', {
        'form': form,
        'proyecto': proyecto
    })

# Función auxiliar para enviar notificaciones de sesión
def enviar_notificacion_sesion(sesion, tipo_notificacion):
    if tipo_notificacion in ['nueva_propuesta', 'horarios_propuestos', 'propuesta_aceptada']:
        destinatario = sesion.proyecto.usuario if sesion.creada_por.groups.filter(name='Tutor').exists() else sesion.creada_por
    else:
        destinatario = sesion.creada_por
    
    plantillas = {
        'nueva_propuesta': {
            'asunto': f'Nueva propuesta de sesión para {sesion.proyecto.nombre_proyecto}',
            'template': 'emails/nueva_propuesta_sesion.html'
        },
        'sesion_confirmada': {
            'asunto': f'Sesión confirmada para {sesion.proyecto.nombre_proyecto}',
            'template': 'emails/sesion_confirmada.html'
        },
    }
    
    if tipo_notificacion in plantillas:
        config = plantillas[tipo_notificacion]
        contexto = {'sesion': sesion, 'destinatario': destinatario}
        contenido = render_to_string(config['template'], contexto)
        
        try:
            send_mail(
                config['asunto'],
                '',
                settings.DEFAULT_FROM_EMAIL,
                [destinatario.email],
                html_message=contenido,
                fail_silently=False
            )
        except Exception as e:
            print(f"Error enviando email: {e}")


# Vista para ver el detalle de una sesión de mentoría
@login_required
def detalle_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionMentoria, id=sesion_id)
    # Verificar que el usuario tiene permisos para ver esta sesión
    if not (request.user == sesion.creada_por or 
            (hasattr(request.user, 'tutor') and sesion.proyecto in request.user.tutor.proyectos_asignados.all()) or
            request.user == sesion.proyecto.usuario):
        messages.error(request, "No tienes permisos para ver esta sesión.")
        return redirect('panel_usuario')
    
    return render(request, 'emprendedores/sesiones/detalle_sesion.html', {'sesion': sesion})

def banco_problemas(request):
    # Obtener los años disponibles
    años = BancoProblema.objects.values_list('año', flat=True).distinct().order_by('-año')
    
    # Obtener el año seleccionado (por defecto el año más reciente)
    año_seleccionado = request.GET.get('año')
    if año_seleccionado:
        año_seleccionado = int(año_seleccionado)
    else:
        año_seleccionado = años.first() if años else timezone.now().year
    
    # Obtener los problemas del año seleccionado
    problemas = BancoProblema.objects.filter(año=año_seleccionado).order_by('numero')
    
    # Estadísticas
    total_problemas = problemas.count()
    problemas_resueltos = problemas.filter(resuelto=True).count()
    problemas_pendientes = total_problemas - problemas_resueltos
    
    return render(request, 'emprendedores/banco_problemas.html', {
        'años': años,
        'año_seleccionado': año_seleccionado,
        'problemas': problemas,
        'total_problemas': total_problemas,
        'problemas_resueltos': problemas_resueltos,
        'problemas_pendientes': problemas_pendientes,
    })
    
@login_required
def gestionar_banco_problemas(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('banco_problemas')
    
    problemas = BancoProblema.objects.all().order_by('-año', 'numero')
    return render(request, 'emprendedores/gestionar_banco_problemas.html', {'problemas': problemas})

@login_required
def agregar_problema(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('banco_problemas')
    
    if request.method == 'POST':
        form = BancoProblemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problema agregado correctamente.')
            return redirect('gestionar_banco_problemas')
    else:
        form = BancoProblemaForm()
    
    return render(request, 'emprendedores/agregar_problema.html', {'form': form})

@login_required
def editar_problema(request, problema_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('banco_problemas')
    
    problema = get_object_or_404(BancoProblema, id=problema_id)
    if request.method == 'POST':
        form = BancoProblemaForm(request.POST, instance=problema)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problema actualizado correctamente.')
            return redirect('gestionar_banco_problemas')
    else:
        form = BancoProblemaForm(instance=problema)
    
    return render(request, 'emprendedores/editar_problema.html', {'form': form, 'problema': problema})

@login_required
def eliminar_problema(request, problema_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('banco_problemas')
    
    problema = get_object_or_404(BancoProblema, id=problema_id)
    if request.method == 'POST':
        problema.delete()
        messages.success(request, 'Problema eliminado correctamente.')
        return redirect('gestionar_banco_problemas')
    
    return render(request, 'emprendedores/eliminar_problema.html', {'problema': problema})


@login_required
def responder_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionMentoria, id=sesion_id)

    if request.method == 'POST':
        accion = request.POST.get('accion', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()

        if accion == 'aceptar':
            sesion.estado = 'confirmada'
            sesion.save()
            messages.success(request, "Sesión confirmada correctamente.")

            # Notificar al creador de la sesión
            if request.user != sesion.creada_por:
                Mensaje.objects.create(
                    remitente=request.user,
                    destinatario=sesion.creada_por,
                    tipo_destinatario='tutor' if hasattr(sesion.creada_por, 'tutor') else 'emprendedor',
                    asunto=f'Sesión confirmada: {sesion.proyecto.nombre_proyecto}',
                    contenido=f'La sesión del proyecto "{sesion.proyecto.nombre_proyecto}" ha sido confirmada para el {sesion.fecha_propuesta.strftime("%d/%m/%Y %H:%M")}.',
                )

        elif accion == 'rechazar':
            if not mensaje:
                messages.error(request, "Debes indicar el motivo de la cancelación.")
                return redirect('detalle_sesion', sesion_id=sesion.id)
            sesion.estado = 'cancelada'
            sesion.motivo_rechazo = mensaje
            sesion.save()
            messages.success(request, "Sesión cancelada correctamente.")

            # Notificar al emprendedor
            if sesion.proyecto.usuario:
                Mensaje.objects.create(
                    remitente=request.user,
                    destinatario=sesion.proyecto.usuario,
                    tipo_destinatario='emprendedor',
                    asunto=f'Sesión cancelada: {sesion.proyecto.nombre_proyecto}',
                    contenido=f'La sesión del proyecto "{sesion.proyecto.nombre_proyecto}" ha sido cancelada.\n\nMotivo: {mensaje}',
                )

        return redirect('panel_tutor')

    return redirect('panel_tutor')

@login_required
def proponer_horarios(request, sesion_id):
    sesion = get_object_or_404(SesionMentoria, id=sesion_id)

    if not (request.user == sesion.creada_por or
            request.user == sesion.proyecto.usuario or
            (hasattr(request.user, 'tutor') and sesion.proyecto.tutor == request.user.tutor)):
        messages.error(request, "No tienes permisos para proponer horarios para esta sesión.")
        return redirect('panel_usuario')

    if request.method == 'POST':
        fecha1 = request.POST.get('fecha_propuesta_1', '').strip()
        duracion = request.POST.get('duracion', '60').strip()
        mensaje = request.POST.get('mensaje', '').strip()

        if not fecha1:
            messages.error(request, "Debes indicar al menos una fecha.")
            return redirect('panel_tutor')

        try:
            PropuestaHorario.objects.create(
                sesion=sesion,
                fecha_propuesta=fecha1,
                duracion=int(duracion),
                propuesto_por=request.user,
                mensaje=mensaje,
            )

            sesion.estado = 'reprogramacion_solicitada'
            sesion.save()

            EventoSesion.objects.create(
                sesion=sesion,
                usuario=request.user,
                accion='proponer_horarios',
                detalles=f"Nuevo horario propuesto: {fecha1}. Motivo: {mensaje}"
            )

            # Notificar a la otra parte
            if request.user == sesion.proyecto.usuario:
                destinatario = sesion.proyecto.tutor.usuario if sesion.proyecto.tutor else None
            else:
                destinatario = sesion.proyecto.usuario

            if destinatario:
                Mensaje.objects.create(
                    remitente=request.user,
                    destinatario=destinatario,
                    tipo_destinatario='tutor' if hasattr(destinatario, 'tutor') else 'emprendedor',
                    asunto=f'Solicitud de reagendamiento: {sesion.proyecto.nombre_proyecto}',
                    contenido=(
                        f'Se ha solicitado reagendar la sesión del proyecto "{sesion.proyecto.nombre_proyecto}".\n\n'
                        f'Nueva fecha propuesta: {fecha1}\nMotivo: {mensaje}'
                    ),
                )

            messages.success(request, "Propuesta de reagendamiento enviada correctamente.")
        except Exception as e:
            messages.error(request, f'Error al proponer horario: {str(e)}')

    return redirect('panel_tutor')

@login_required
def aceptar_propuesta_horario(request, propuesta_id):
    propuesta = get_object_or_404(PropuestaHorario, id=propuesta_id)
    sesion = propuesta.sesion
    
    # Verificar permisos - solo el creador de la sesión o el tutor/emprendedor relacionado pueden aceptar propuestas
    if not (request.user == sesion.creada_por or 
            (hasattr(request.user, 'tutor') and sesion.proyecto.tutor == request.user.tutor) or
            request.user == sesion.proyecto.usuario):
        messages.error(request, "No tienes permisos para aceptar esta propuesta.")
        return redirect('panel_usuario')
    
    if request.method == 'POST':
        # Actualizar la sesión con los nuevos datos de la propuesta
        sesion.fecha_propuesta = propuesta.fecha_propuesta
        sesion.duracion = propuesta.duracion
        sesion.estado = 'confirmada'
        sesion.save()
        
        # Marcar la propuesta como aceptada
        propuesta.aceptada = True
        propuesta.save()
        
        # Registrar evento
        EventoSesion.objects.create(
            sesion=sesion,
            usuario=request.user,
            accion='aceptar_propuesta_horario',
            detalles=f"Propuesta de horario aceptada: {propuesta.fecha_propuesta} por {propuesta.duracion} minutos."
        )
        
        messages.success(request, "Propuesta de horario aceptada. La sesión ha sido reprogramada.")
        return redirect('detalle_sesion', sesion_id=sesion.id)
    
    # Si es GET, mostrar página de confirmación
    return render(request, 'emprendedores/sesiones/aceptar_propuesta.html', {'propuesta': propuesta})    

@login_required
def subir_archivo_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionMentoria, id=sesion_id)
    
    # Verificar permisos - solo participantes de la sesión pueden subir archivos
    if not (request.user == sesion.creada_por or 
            request.user == sesion.proyecto.usuario or
            (hasattr(request.user, 'tutor') and sesion.proyecto.tutor == request.user.tutor)):
        messages.error(request, "No tienes permisos para subir archivos a esta sesión.")
        return redirect('panel_usuario')
    
    if request.method == 'POST':
        form = ArchivoSesionForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.sesion = sesion
            archivo.subido_por = request.user
            archivo.save()
            
            # Registrar evento
            EventoSesion.objects.create(
                sesion=sesion,
                usuario=request.user,
                accion='subir_archivo',
                detalles=f"Archivo subido: {archivo.archivo.name}"
            )
            
            messages.success(request, "Archivo subido correctamente.")
            return redirect('detalle_sesion', sesion_id=sesion.id)
    else:
        form = ArchivoSesionForm()
    
    return render(request, 'emprendedores/sesiones/subir_archivo.html', {
        'form': form,
        'sesion': sesion
    })


@login_required
def marcar_sesion_realizada(request, sesion_id):
    sesion = get_object_or_404(SesionMentoria, id=sesion_id)
    
    # Verificar permisos - solo participantes de la sesión pueden marcarla como realizada
    if not (request.user == sesion.creada_por or 
            request.user == sesion.proyecto.usuario or
            (hasattr(request.user, 'tutor') and sesion.proyecto.tutor == request.user.tutor)):
        messages.error(request, "No tienes permisos para marcar esta sesión como realizada.")
        return redirect('panel_usuario')
    
    if request.method == 'POST':
        # Cambiar el estado de la sesión a realizada
        sesion.estado = 'realizada'
        sesion.save()
        
        # Registrar evento
        EventoSesion.objects.create(
            sesion=sesion,
            usuario=request.user,
            accion='marcar_sesion_realizada',
            detalles="Sesión marcada como realizada."
        )
        
        messages.success(request, "Sesión marcada como realizada correctamente.")
        return redirect('detalle_sesion', sesion_id=sesion.id)
    
    # Si es GET, mostrar página de confirmación
    return render(request, 'emprendedores/sesiones/marcar_realizada.html', {'sesion': sesion})    


@login_required
def listar_sesiones_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Verificar permisos - solo el tutor asignado o el emprendedor dueño del proyecto pueden ver las sesiones
    if not (request.user == proyecto.usuario or 
            (hasattr(request.user, 'tutor') and proyecto.tutor == request.user.tutor)):
        messages.error(request, "No tienes permisos para ver las sesiones de este proyecto.")
        return redirect('panel_usuario')
    
    sesiones = SesionMentoria.objects.filter(proyecto=proyecto).order_by('-fecha_propuesta')
    
    return render(request, 'emprendedores/sesiones/listar_sesiones.html', {
        'proyecto': proyecto,
        'sesiones': sesiones
    })

@login_required
def ver_mensajes(request):
    
    mensajes = Mensaje.objects.filter(destinatario=request.user).order_by('-fecha_envio')
    
    return render(request, 'emprendedores/ver_mensajes.html', {
        'mensajes': mensajes
    })
@require_POST
@login_required
def marcar_mensaje_leido(request, mensaje_id):
    try:
        mensaje = get_object_or_404(Mensaje, id=mensaje_id, destinatario=request.user)
        mensaje.leido = True
        mensaje.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def lista_proyectos(request):
    if not request.user.is_superuser:
        return redirect('panel_usuario')

    proyectos = Proyecto.objects.all()

    # Filtro por estado
    estado_filter = request.GET.get('estado', '')
    if estado_filter:
        proyectos = proyectos.filter(estado=estado_filter)

    # Filtro por presupuesto (rango)
    presupuesto_min = request.GET.get('presupuesto_min', '')
    presupuesto_max = request.GET.get('presupuesto_max', '')
    if presupuesto_min:
        proyectos = proyectos.filter(presupuesto_estimado__gte=presupuesto_min)
    if presupuesto_max:
        proyectos = proyectos.filter(presupuesto_estimado__lte=presupuesto_max)

    # Filtro por fecha de creación (rango)
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    if fecha_desde:
        proyectos = proyectos.filter(fecha_registro__date__gte=fecha_desde)
    if fecha_hasta:
        proyectos = proyectos.filter(fecha_registro__date__lte=fecha_hasta)

    return render(request, 'emprendedores/lista_proyectos.html', {
        'proyectos': proyectos,
        'estados_proyecto': Proyecto.ESTADOS,
        'estado_filter': estado_filter,
        'presupuesto_min': presupuesto_min,
        'presupuesto_max': presupuesto_max,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })

@login_required
def lista_tutores(request):
    if not request.user.is_superuser:
        return redirect('panel_usuario')
    tutores = Tutor.objects.all()
    return render(request, 'emprendedores/lista_tutores.html', {'tutores': tutores})


@login_required
def lista_emprendedores(request):
    if not request.user.is_superuser:
        return redirect('panel_usuario')
    tutor_user_ids = Tutor.objects.values_list('usuario_id', flat=True)
    emprendedores = User.objects.filter(is_superuser=False).exclude(id__in=tutor_user_ids)
    for emprendedor in emprendedores:
        emprendedor.num_proyectos = Proyecto.objects.filter(usuario=emprendedor).count()
        if not hasattr(emprendedor, 'emprendedor_profile'):
            EmprendedorProfile.objects.create(user=emprendedor)
    return render(request, 'emprendedores/lista_emprendedores.html', {'emprendedores': emprendedores})


@login_required
def lista_proyectos(request):
    if not request.user.is_superuser:
        return redirect('panel_usuario')
    proyectos = Proyecto.objects.all()
    return render(request, 'emprendedores/lista_proyectos.html', {'proyectos': proyectos})    



#  crear tareas de forma manual 
@login_required
def crear_tarea_tutor(request):
    if not hasattr(request.user, 'tutor'):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('panel_usuario')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        prioridad = request.POST.get('prioridad', 'media')
        proyecto_id = request.POST.get('proyecto_id')
        dias_limite = request.POST.get('dias_limite', '7')
        
        if titulo and proyecto_id:
            proyecto = get_object_or_404(Proyecto, id=proyecto_id, tutor=request.user.tutor)
            try:
                dias = int(dias_limite)
                if dias < 1:
                    dias = 1
            except ValueError:
                dias = 7
            
            Tarea.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prioridad,
                fecha_limite=timezone.now() + timedelta(days=dias),
                completada=False,
                proyecto=proyecto,
                asignada_a=request.user,
            )
            messages.success(request, f'Tarea "{titulo}" creada correctamente.')
        else:
            messages.error(request, 'El título y el proyecto son obligatorios.')
    
    return redirect('panel_tutor')


@login_required
def bandeja_tutor(request):
    if not hasattr(request.user, 'tutor'):
        return redirect('panel_usuario')

    # Mensajes recibidos por el tutor
    mensajes_recibidos = Mensaje.objects.filter(
        destinatario=request.user
    ).order_by('-fecha_envio')

    # Mensajes enviados por el tutor
    mensajes_enviados = Mensaje.objects.filter(
        remitente=request.user
    ).order_by('-fecha_envio')

    # Cantidad de no leídos para el badge
    no_leidos = mensajes_recibidos.filter(leido=False).count()

    # Lista de usuarios a quienes puede enviar mensajes
    tutor = get_object_or_404(Tutor, usuario=request.user)
    proyectos = Proyecto.objects.filter(tutor=tutor)
    emprendedores = User.objects.filter(
        proyectos__in=proyectos
    ).distinct()
    administradores = User.objects.filter(is_superuser=True)

    return render(request, 'emprendedores/bandeja_tutor.html', {
        'mensajes_recibidos': mensajes_recibidos,
        'mensajes_enviados': mensajes_enviados,
        'no_leidos': no_leidos,
        'emprendedores': emprendedores,
        'administradores': administradores,
    })


@login_required
def solicitar_sesion_emprendedor(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
 
    # Solo el emprendedor dueño del proyecto puede solicitar sesiones
    if request.user != proyecto.usuario:
        messages.error(request, "No tienes permisos para solicitar sesiones en este proyecto.")
        return redirect('panel_emprendedor')
 
    # El proyecto debe tener tutor asignado
    if not proyecto.tutor:
        messages.error(request, "Tu proyecto no tiene tutor asignado aún.")
        return redirect('panel_emprendedor')
 
    if request.method == 'POST':
        objetivo = request.POST.get('objetivo', '').strip()
        tipo = request.POST.get('tipo', 'seguimiento').strip()
        fecha_propuesta = request.POST.get('fecha_propuesta', '').strip()
        duracion = request.POST.get('duracion', '60').strip()
        formato = request.POST.get('formato', 'virtual').strip()
        agenda = request.POST.get('agenda', '').strip()
 
        if not objetivo or not fecha_propuesta:
            messages.error(request, "El objetivo y la fecha son obligatorios.")
            return redirect('panel_emprendedor')
 
        try:
            sesion = SesionMentoria.objects.create(
                proyecto=proyecto,
                creada_por=request.user,
                objetivo=objetivo,
                tipo=tipo,
                fecha_propuesta=fecha_propuesta,
                duracion=int(duracion),
                formato=formato,
                agenda=agenda,
                estado='propuesta',
            )
 
            # Registrar evento
            EventoSesion.objects.create(
                sesion=sesion,
                usuario=request.user,
                accion='solicitar_sesion',
                detalles=f"El emprendedor solicitó una sesión: {objetivo}. Fecha propuesta: {fecha_propuesta}."
            )
 
            # Notificar al tutor via mensaje interno
            Mensaje.objects.create(
                remitente=request.user,
                destinatario=proyecto.tutor.usuario,
                tipo_destinatario='tutor',
                asunto=f'Solicitud de sesión: {proyecto.nombre_proyecto}',
                contenido=(
                    f'El emprendedor {request.user.get_full_name()} ha solicitado una sesión de mentoría '
                    f'para el proyecto "{proyecto.nombre_proyecto}".\n\n'
                    f'Objetivo: {objetivo}\n'
                    f'Tipo: {tipo}\n'
                    f'Fecha propuesta: {fecha_propuesta}\n'
                    f'Duración: {duracion} minutos\n'
                    f'Formato: {formato}\n\n'
                    f'Puedes aceptar o rechazar la solicitud desde tu panel.'
                ),
            )
 
            messages.success(request, 'Solicitud de sesión enviada correctamente. Tu tutor la revisará pronto.')
 
        except Exception as e:
            messages.error(request, f'Error al enviar la solicitud: {str(e)}')
 
    return redirect('panel_emprendedor')