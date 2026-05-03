from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Modelo Proyecto
class Proyecto(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('revision', 'En revisión'),
        ('aceptado', 'Aceptado'),
        ('asignado', 'En proceso'),
        ('rechazado', 'Rechazado'),
        ('finalizado', 'Finalizado'),
    )
    
    SECTORES = (
        ('tecnologia', 'Tecnología'),
        ('salud', 'Salud'),
        ('educacion', 'Educación'),
        ('finanzas', 'Finanzas'),
        ('comercio', 'Comercio'),
        ('otros', 'Otros'),
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos', null=True, blank=True)
    nombre_proyecto = models.CharField(max_length=200)
    descripcion = models.TextField()
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    sector = models.CharField(max_length=20, choices=SECTORES, default='tecnologia')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    archivo_proyecto = models.FileField(upload_to='proyectos/%Y/%m/%d/', blank=True, null=True)
    progreso = models.PositiveIntegerField(default=0)
    motivo_rechazo = models.TextField(blank=True, null=True)
    presupuesto_estimado = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        help_text="Presupuesto estimado del proyecto en pesos"
    )

    
    gestor = models.ForeignKey('GestorCiencias', on_delete=models.SET_NULL, null=True, blank=True, 
                            related_name='proyectos_gestionados')
    
    class Meta:
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return self.nombre_proyecto


# Modelo GestorCiencias
class GestorCiencias(models.Model):
    GRADOS_ACADEMICOS = (
        ('tecnico', 'Técnico'),
        ('licenciatura', 'Licenciatura'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado'),
    )
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True)
    grado_academico = models.CharField(max_length=20, choices=GRADOS_ACADEMICOS)
    institucion = models.CharField(max_length=100)
    especialidades = models.TextField()
    experiencia = models.TextField()
    areas_tutorizar = models.TextField(help_text="Lista de áreas en las que puede tutorizar")
    max_proyectos = models.PositiveIntegerField(default=3)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.especialidades}"
    
    @property
    def proyectos_actuales(self):
        return self.proyectos_gestionados.count()
    

# Modelo para el perfil de emprendedor
class EmprendedorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emprendedor_profile')
    gestor = models.ForeignKey(GestorCiencias, on_delete=models.SET_NULL, null=True, blank=True, related_name='emprendedores_asignados')
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


# Modelo Tarea
class Tarea(models.Model):
    PRIORIDADES = (
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    )
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField()
    completada = models.BooleanField(default=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    asignada_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_asignadas')
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo


# Modelo SesionMentoria
class SesionMentoria(models.Model):
    ESTADOS = (
        ('draft', 'Borrador'),
        ('propuesta', 'Propuesta'),
        ('pendiente_confirmacion', 'Pendiente de Confirmación'),
        ('confirmada', 'Confirmada'),
        ('reprogramacion_solicitada', 'Reprogramación Solicitada'),
        ('rescheduled', 'Reprogramada'),
        ('cancelada', 'Cancelada'),
        ('realizada', 'Realizada'),
        ('no_show', 'No Show'),
        ('blocked', 'Bloqueada'),
    )
    
    FORMATOS = (
        ('virtual', 'Virtual'),
        ('presencial', 'Presencial'),
        ('hibrido', 'Híbrido'),
    )
    
    TIPOS = (
        ('revision_inicial', 'Revisión Inicial'),
        ('seguimiento', 'Seguimiento'),
        ('presentacion_avance', 'Presentación de Avance'),
        ('problematica', 'Resolución de Problemática'),
        ('otro', 'Otro'),
    )
    
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='sesiones')
    creada_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sesiones_creadas')
    fecha_propuesta = models.DateTimeField()
    duracion = models.PositiveIntegerField(help_text="Duración en minutos")
    formato = models.CharField(max_length=10, choices=FORMATOS, default='virtual')
    enlace_virtual = models.URLField(blank=True, null=True)
    direccion_presencial = models.CharField(max_length=255, blank=True, null=True)
    objetivo = models.CharField(max_length=200)
    agenda = models.TextField(blank=True)
    estado = models.CharField(max_length=30, choices=ESTADOS, default='draft')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='seguimiento')
    materiales_requeridos = models.TextField(blank=True, help_text="Lista de materiales requeridos")
    es_material_obligatorio = models.BooleanField(default=False)
    motivo_cancelacion = models.TextField(blank=True)
    motivo_rechazo = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    sesion_original = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reprogramaciones')
    contador_reprogramaciones = models.PositiveIntegerField(default=0)
    
    gestor_presente = models.BooleanField(default=False)
    emprendedor_presente = models.BooleanField(default=False)
    minuta = models.TextField(blank=True)
    
    class Meta:
        ordering = ['fecha_propuesta']
    
    def __str__(self):
        return f"Sesión {self.get_tipo_display()} - {self.proyecto.nombre_proyecto} - {self.fecha_propuesta}"
    
    def puede_ser_modificada(self):
        return self.estado in ['draft', 'propuesta', 'pendiente_confirmacion']
    
    def es_confirmada(self):
        return self.estado == 'confirmada'
    
    def necesita_materiales(self):
        return self.materiales_requeridos and self.es_material_obligatorio
    
    def materiales_subidos(self):
        return self.archivos.exists()
    
    def tiene_conflicto_agenda(self):
        from django.db.models import Q
        fecha_fin = self.fecha_propuesta + timezone.timedelta(minutes=self.duracion)
        
        conflicto_gestor = SesionMentoria.objects.filter(
            Q(proyecto__gestores=self.creada_por.gestor) | Q(creada_por=self.creada_por),
            estado='confirmada',
            fecha_propuesta__lt=fecha_fin,
            fecha_propuesta__gt=self.fecha_propuesta - timezone.timedelta(minutes=self.duracion)
        ).exclude(id=self.id).exists()
        
        conflicto_emprendedor = SesionMentoria.objects.filter(
            proyecto=self.proyecto,
            estado='confirmada',
            fecha_propuesta__lt=fecha_fin,
            fecha_propuesta__gt=self.fecha_propuesta - timezone.timedelta(minutes=self.duracion)
        ).exclude(id=self.id).exists()
        
        return conflicto_gestor or conflicto_emprendedor


class ArchivoSesion(models.Model):
    sesion = models.ForeignKey(SesionMentoria, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='materiales_sesiones/%Y/%m/%d/')
    subido_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_subido = models.DateTimeField(auto_now_add=True)
    es_material_obligatorio = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Archivo {self.archivo.name} para {self.sesion}"


class EventoSesion(models.Model):
    sesion = models.ForeignKey(SesionMentoria, on_delete=models.CASCADE, related_name='eventos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True)
    estado_anterior = models.CharField(max_length=30, blank=True)
    estado_nuevo = models.CharField(max_length=30, blank=True) 
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.timestamp}"


class PropuestaHorario(models.Model):
    sesion = models.ForeignKey(SesionMentoria, on_delete=models.CASCADE, related_name='propuestas_horario')
    fecha_propuesta = models.DateTimeField()
    duracion = models.PositiveIntegerField(default=60)
    propuesto_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    mensaje = models.TextField(blank=True)
    aceptada = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['fecha_propuesta']
    
    def __str__(self):
        return f"Propuesta {self.fecha_propuesta} para {self.sesion}"


# Modelo Mensaje
class Mensaje(models.Model):
    TIPOS_DESTINATARIO = (
        ('gestor', 'Gestor de Ciencias'),
        ('emprendedor', 'Emprendedor'),
        ('administrador', 'Administrador'),
    )
    
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    tipo_destinatario = models.CharField(max_length=20, choices=TIPOS_DESTINATARIO)
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    archivo = models.FileField(upload_to='mensajes/%Y/%m/%d/', blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"Mensaje de {self.remitente} para {self.destinatario} - {self.asunto}"


#  Forum Evento
class Convocatoria(models.Model):
    titulo = models.CharField(max_length=200, default="Convocatoria al Forum de Ciencias Técnicas e Innovación de Desoft Santiago de Cuba")
    fecha_inicio = models.DateTimeField()
    fecha_cierre = models.DateTimeField()
    objetivos = models.TextField()
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    convocatoria = models.ForeignKey(Convocatoria, on_delete=models.CASCADE, related_name='categorias')

    def __str__(self):
        return self.nombre

class DocumentoPlantilla(models.Model):
    TIPO_DOCUMENTO = (
        ('ponencia', 'Plantilla de Ponencia'),
        ('ficha_tecnica', 'Formulario de Ficha Técnica'),
        ('aval', 'Formulario de Aval'),
    )
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_DOCUMENTO)
    archivo = models.FileField(upload_to='plantillas/')
    descripcion = models.TextField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre        

class MiembroComision(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    preside_comite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cargo}"

class Comision(models.Model):
    nombre = models.CharField(max_length=100)
    presidente = models.ForeignKey(MiembroComision, on_delete=models.CASCADE, related_name='comisiones_presididas')
    integrantes = models.ManyToManyField(MiembroComision, related_name='comisiones', blank=True)

    def __str__(self):
        return self.nombre        

class ProgramaForum(models.Model):
    horario = models.CharField(max_length=100)
    actividad = models.CharField(max_length=200)
    responsable = models.CharField(max_length=100)
    trabajo = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.horario} - {self.actividad}"        

class TrabajoInnovacion(models.Model):
    año = models.IntegerField()
    categoria = models.CharField(max_length=100)
    trabajo = models.CharField(max_length=200)
    reconocimiento = models.CharField(max_length=200, blank=True, null=True)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.trabajo} ({self.año})" 

class ResumenInnovacion(models.Model):
    año = models.IntegerField()
    categoria = models.CharField(max_length=100)
    trabajo = models.CharField(max_length=200)
    reconocimiento = models.CharField(max_length=200, blank=True, null=True)
    gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    participantes = models.TextField(blank=True, null=True, help_text="Nombres de los participantes")
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.trabajo} ({self.año})"
    
    class Meta:
        verbose_name_plural = "Resúmenes de innovación"
        ordering = ['-año', 'categoria']

class ParticipanteForum(models.Model):
    CATEGORIA_OCUPACIONAL_CHOICES = (
        ('trabajador', 'Trabajador'),
        ('colaborador_externo', 'Colaborador Externo'),
        ('estudiante', 'Estudiante'),
        ('otro', 'Otro'),
    )

    RELACION_EMPRESA_CHOICES = (
        ('trabajador', 'Trabajador'),
        ('colaborador', 'Colaborador'),
        ('estudiante', 'Estudiante'),
        ('externo', 'Externo'),
    )

    nombre_completo = models.CharField(max_length=200)
    carne_identidad = models.CharField(max_length=11, unique=True)
    categoria_ocupacional = models.CharField(max_length=20, choices=CATEGORIA_OCUPACIONAL_CHOICES)
    centro_trabajo = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100)
    relacion_empresa = models.CharField(max_length=20, choices=RELACION_EMPRESA_CHOICES)
    
    # Campos para los archivos
    ponencia = models.FileField(upload_to='ponencias/%Y/%m/%d/')
    ficha_tecnica = models.FileField(upload_to='fichas_tecnicas/%Y/%m/%d/')
    avales = models.FileField(upload_to='avales/%Y/%m/%d/')
    presentacion = models.FileField(upload_to='presentaciones/%Y/%m/%d/')
    
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    numero_expediente = models.CharField(max_length=20, unique=True, blank=True)
    evaluado = models.BooleanField(default=False)
    aceptado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_completo} - {self.numero_expediente}"

    def save(self, *args, **kwargs):
        if not self.numero_expediente:
            # Generar número de expediente único
            año = timezone.now().year
            ultimo_expediente = ParticipanteForum.objects.filter(
                numero_expediente__startswith=str(año)
            ).order_by('numero_expediente').last()
            
            if ultimo_expediente:
                ultimo_numero = int(ultimo_expediente.numero_expediente.split('-')[1])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
                
            self.numero_expediente = f"{año}-{nuevo_numero:04d}"
        super().save(*args, **kwargs)

class ConfiguracionCorreo(models.Model):
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {'Activo' if self.activo else 'Inactivo'}"

    def save(self, *args, **kwargs):
        # Si se marca como activo, desactivar los demás
        if self.activo:
            ConfiguracionCorreo.objects.filter(activo=True).exclude(id=self.id).update(activo=False)
        super().save(*args, **kwargs)


class BancoProblema(models.Model):
    PRIORIDAD_CHOICES = (
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    )
    
    año = models.IntegerField()
    numero = models.IntegerField()
    objetivo = models.TextField()
    problema = models.TextField()
    ponencia_consultar = models.CharField(max_length=200, blank=True, null=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    resuelto = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('año', 'numero')
        ordering = ['-año', 'numero']

    def __str__(self):
        return f"Problema {self.numero} - {self.año}"        

class SolicitudVentanilla(models.Model):
    TIPOS = (
        ('proyecto', 'Solicitud de Proyecto'),
        ('demanda', 'Demanda Tecnológica'),
        ('empleo', 'Solicitud de Empleo'),
    )
    ESTADOS = (
        ('recibida', 'Recibida'),
        ('en_revision', 'En Revisión'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='recibida')
    nombre_contacto = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    nombre_proyecto = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField()
    area_interes = models.CharField(max_length=200, blank=True)
    documentacion = models.FileField(upload_to='ventanilla/%Y/%m/', blank=True, null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    numero_expediente = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']

    def save(self, *args, **kwargs):
        if not self.numero_expediente:
            import random, string
            self.numero_expediente = 'DSF-' + ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre_contacto} ({self.numero_expediente})"