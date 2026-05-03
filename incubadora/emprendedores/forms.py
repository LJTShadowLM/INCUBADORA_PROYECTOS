from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import SesionMentoria, ArchivoSesion, PropuestaHorario, Proyecto, GestorCiencias, Convocatoria, Categoria, DocumentoPlantilla, TrabajoInnovacion, ResumenInnovacion, ParticipanteForum, ConfiguracionCorreo, BancoProblema
from django.utils import timezone


class SesionMentoriaForm(forms.ModelForm):
    class Meta:
        model = SesionMentoria
        fields = [
            'fecha_propuesta', 'duracion', 'formato', 'tipo', 'objetivo', 
            'agenda', 'materiales_requeridos', 'es_material_obligatorio',
            'enlace_virtual', 'direccion_presencial'
        ]
        widgets = {
            'fecha_propuesta': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'step': '15'}),
            'formato': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'materiales_requeridos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'enlace_virtual': forms.URLInput(attrs={'class': 'form-control'}),
            'direccion_presencial': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'fecha_propuesta': 'Fecha y hora propuesta',
            'duracion': 'Duración (minutos)',
            'formato': 'Formato de la sesión',
            'tipo': 'Tipo de sesión',
            'objetivo': 'Objetivo de la sesión',
            'agenda': 'Agenda or temas a tratar',
            'materiales_requeridos': 'Materiales requeridos',
            'es_material_obligatorio': '¿Es obligatorio entregar estos materiales antes de la sesión?',
            'enlace_virtual': 'Enlace para sesión virtual',
            'direccion_presencial': 'Dirección para sesión presencial',
        }

    def __init__(self, *args, **kwargs):
        self.proyecto = kwargs.pop('proyecto', None)
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Establecer valores iniciales
        self.fields['duracion'].initial = 60
        self.fields['formato'].initial = 'virtual'
        self.fields['tipo'].initial = 'seguimiento'

    def clean_fecha_propuesta(self):
        fecha_propuesta = self.cleaned_data.get('fecha_propuesta')
        if fecha_propuesta and fecha_propuesta < timezone.now():
            raise ValidationError("La fecha y hora propuesta no puede ser en el pasado.")
        return fecha_propuesta

    def clean(self):
        cleaned_data = super().clean()
        formato = cleaned_data.get('formato')
        enlace_virtual = cleaned_data.get('enlace_virtual')
        direccion_presencial = cleaned_data.get('direccion_presencial')
        
        if formato == 'virtual' and not enlace_virtual:
            self.add_error('enlace_virtual', 'Debe proporcionar un enlace para sesiones virtuales.')
        
        if formato == 'presencial' and not direccion_presencial:
            self.add_error('direccion_presencial', 'Debe proporcionar una dirección para sesiones presenciales.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proyecto:
            instance.proyecto = self.proyecto
        if self.usuario:
            instance.creada_por = self.usuario
        
        if commit:
            instance.save()
        return instance


class ArchivoSesionForm(forms.ModelForm):
    class Meta:
        model = ArchivoSesion
        fields = ['archivo', 'es_material_obligatorio']
        widgets = {
            'archio': forms.FileInput(attrs={'class': 'form-control'}),
            'es_material_obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropuestaHorarioForm(forms.ModelForm):
    fecha_propuesta_1 = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Primera opción de horario"
    )
    fecha_propuesta_2 = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Segunda opción de horario (opcional)",
        required=False
    )
    fecha_propuesta_3 = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Tercera opción de horario (opcional)",
        required=False
    )
    duracion = forms.IntegerField(
        min_value=15, max_value=240, initial=60,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'step': '15'}),
        label="Duración (minutos)"
    )
    
    class Meta:
        model = PropuestaHorario
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Explique por qué necesita reprogramar la sesión...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha1 = cleaned_data.get('fecha_propuesta_1')
        fecha2 = cleaned_data.get('fecha_propuesta_2')
        fecha3 = cleaned_data.get('fecha_propuesta_3')
        
        if fecha1 and fecha1 < timezone.now():
            self.add_error('fecha_propuesta_1', 'La fecha y hora no puede ser en el pasado.')
        
        fechas = [f for f in [fecha1, fecha2, fecha3] if f]
        if len(fechas) != len(set(fechas)):
            self.add_error('fecha_propuesta_2', 'Las opciones de horario deben ser diferentes.')
        
        return cleaned_data


class ResponderSesionForm(forms.Form):
    ACCIONES = (
        ('aceptar', 'Aceptar sesión'),
        ('rechazar', 'Rechazar sesión'),
        ('reprogramar', 'Proponer otro horario'),
    )
    
    accion = forms.ChoiceField(
        choices=ACCIONES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="¿Qué desea hacer con esta sesión?"
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Agregue un mensaje opcional...'}),
        required=False,
        label="Mensaje (opcional)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accion'].widget.attrs.update({'onchange': 'toggleReprogramacion(this)'})


class MinutaSesionForm(forms.Form):
    minuta = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label="Minuta de la sesión"
    )
    gestor_presente = forms.BooleanField(
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Gestor de Ciencias presente"
    )
    emprendedor_presente = forms.BooleanField(
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Emprendedor presente"
    )


class RegistroUsuarioProyectoForm(forms.Form):
    # Campos para el usuario
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar contraseña")
    
    # Campos para el proyecto y datos personales
    nombre_completo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre_proyecto = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    sector = forms.ChoiceField(choices=Proyecto.SECTORES, widget=forms.Select(attrs={'class': 'form-control'}))
    archivo_proyecto = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    presupuesto_estimado = forms.DecimalField(
        max_digits=12, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ej: 15000.00'}),
        label="Presupuesto Estimado ($)"
    )
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        
        return cleaned_data


class GestorCienciasRegistrationForm(forms.Form):
    # Campos para el usuario
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre de usuario"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar contraseña"
    )
    
    # Campos para el gestor
    nombre_completo = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre completo"
    )
    
    telefono = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Teléfono"
    )
    cedula = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Cédula de identidad"
    )
    grado_academico = forms.ChoiceField(
        choices=GestorCiencias.GRADOS_ACADEMICOS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Grado académico"
    )
    institucion = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Institución de procedencia"
    )
    especialidades = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Especialidades"
    )
    experiencia = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Experiencia"
    )
    areas_tutorizar = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Áreas que puede tutorizar"
    )
    max_proyectos = forms.IntegerField(
        initial=3,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Máximo número de proyectos"
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        # Si estamos editando, hacer que los campos de contraseña no sean obligatorios
        if self.instance:
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Si estamos editando, excluir el usuario actual de la validación
        if self.instance:
            if User.objects.filter(username=username).exclude(pk=self.instance.usuario.pk).exists():
                raise ValidationError("Este nombre de usuario ya está en uso.")
        else:
            # Para creación nueva, validar normalmente
            if User.objects.filter(username=username).exists():
                raise ValidationError("Este nombre de usuario ya está en uso.")
                
        return username

    def clean(self):
        cleaned_data = super().clean()
        
        # Solo validar coincidencia de contraseñas si se proporcionaron
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self):
        # Crear usuario sin email
        user_data = {
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
            'first_name': self.cleaned_data['nombre_completo'].split()[0],
            'last_name': ' '.join(self.cleaned_data['nombre_completo'].split()[1:]),
        }
        
        # Si estamos editando, actualizar el usuario existente
        if self.instance:
            user = self.instance.usuario
            user.username = user_data['username']
            if user_data['password']:
                user.set_password(user_data['password'])
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.save()
            
            gestor = self.instance
        else:
            # Crear nuevo usuario
            user = User.objects.create_user(**user_data)
            
            # Crear gestor
            gestor = GestorCiencias.objects.create(
                usuario=user,
                cedula=self.cleaned_data['cedula'],
                grado_academico=self.cleaned_data['grado_academico'],
                institucion=self.cleaned_data['institucion'],
                especialidades=self.cleaned_data['especialidades'],
                experiencia=self.cleaned_data['experiencia'],
                areas_tutorizar=self.cleaned_data['areas_tutorizar'],
                max_proyectos=self.cleaned_data['max_proyectos'],
                telefono=self.cleaned_data['telefono'],
            )
        
        # Actualizar los campos del gestor
        gestor.telefono = self.cleaned_data['telefono']
        gestor.cedula = self.cleaned_data['cedula']
        gestor.grado_academico = self.cleaned_data['grado_academico']
        gestor.institucion = self.cleaned_data['institucion']
        gestor.especialidades = self.cleaned_data['especialidades']
        gestor.experiencia = self.cleaned_data['experiencia']
        gestor.areas_tutorizar = self.cleaned_data['areas_tutorizar']
        gestor.max_proyectos = self.cleaned_data['max_proyectos']
        gestor.save()
        
        return gestor


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre_proyecto', 'descripcion', 'sector', 'archivo_proyecto', 'nombre_completo', 'email', 'telefono']
        widgets = {
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sector': forms.Select(attrs={'class': 'form-control'}),
            'archivo_proyecto': forms.FileInput(attrs={'class': 'form-control'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.is_authenticated:
            # Prellenar con datos del usuario si está disponible
            self.fields['nombre_completo'].initial = self.user.get_full_name()
            self.fields['email'].initial = self.user.email        


class MensajeForm(forms.Form):
    TIPOS_DESTINATARIO = (
        ('tutor', 'Gestor de Ciencias'),
        ('emprendedor', 'Emprendedor'),
        ('administrador', 'Administrador'),
    )
    
    tipo_destinatario = forms.ChoiceField(
        choices=TIPOS_DESTINATARIO,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Enviar a:"
    )
    destinatario_id = forms.IntegerField(widget=forms.HiddenInput())
    asunto = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Asunto"
    )
    contenido = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label="Mensaje"
    )

# Nota: hay una clase ProyectoForm duplicada, la mantengo igual
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre_proyecto', 'descripcion', 'sector', 'archivo_proyecto', 'nombre_completo', 'email', 'telefono']
        widgets = {
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sector': forms.Select(attrs={'class': 'form-control'}),
            'archivo_proyecto': forms.FileInput(attrs={'class': 'form-control'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_proyecto': 'Nombre del Proyecto',
            'descripcion': 'Descripción',
            'sector': 'Sector',
            'archivo_proyecto': 'Archivo del Proyecto (opcional)',
            'nombre_completo': 'Nombre Completo',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono (opcional)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Prellenar con datos del usuario si está disponible
            self.fields['nombre_completo'].initial = self.user.get_full_name()
            self.fields['email'].initial = self.user.email


class ConvocatoriaForm(forms.ModelForm):
    class Meta:
        model = Convocatoria
        fields = ['titulo', 'fecha_inicio', 'fecha_cierre', 'objetivos', 'activa']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_cierre': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'titulo': 'Título de la Convocatoria',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_cierre': 'Fecha de Cierre',
            'objetivos': 'Objetivos de la Convocatoria',
            'activa': 'Convocatoria Activa'
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DocumentoPlantillaForm(forms.ModelForm):
    class Meta:
        model = DocumentoPlantilla
        fields = ['nombre', 'tipo', 'archivo', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class TrabajoInnovacionForm(forms.ModelForm):
    class Meta:
        model = TrabajoInnovacion
        fields = ['año', 'categoria', 'trabajo', 'reconocimiento', 'gasto']
        widgets = {
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'reconocimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'gasto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ResumenInnovacionForm(forms.ModelForm):
    class Meta:
        model = ResumenInnovacion
        fields = ['año', 'categoria', 'trabajo', 'reconocimiento', 'gasto', 'participantes', 'observaciones']
        widgets = {
            'año': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'max': '2030'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'trabajo': forms.TextInput(attrs={'class': 'form-control'}),
            'reconocimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'gasto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'participantes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'año': 'Año de presentación',
            'categoria': 'Categoría del trabajo',
            'trabajo': 'Nombre del trabajo',
            'reconocimiento': 'Reconocimiento obtenido',
            'gasto': 'Gasto invertido ($)',
            'participantes': 'Participantes',
            'observaciones': 'Observaciones adicionales',
        }

class ParticipanteForumForm(forms.ModelForm):
    ponencia = forms.FileField(
        label='Ponencia (PDF)',
        widget=forms.FileInput(attrs={'accept': '.pdf'}),
        help_text='Documento PDF con la ponencia completa. Máximo 10MB.'
    )
    ficha_tecnica = forms.FileField(
        label='Ficha Técnica (PDF)',
        widget=forms.FileInput(attrs={'accept': '.pdf'}),
        help_text='Formulario de ficha técnica en PDF. Máximo 5MB.'
    )
    avales = forms.FileField(
        label='Avales (PDF)',
        widget=forms.FileInput(attrs={'accept': '.pdf'}),
        help_text='Documentos de aval en PDF. Máximo 5MB.'
    )
    presentacion = forms.FileField(
        label='Presentación (PPT/PPTX)',
        widget=forms.FileInput(attrs={'accept': '.ppt,.pptx'}),
        help_text='Presentación para exposición oral. Máximo 20MB.'
    )

    class Meta:
        model = ParticipanteForum
        fields = [
            'nombre_completo', 'carne_identidad', 'categoria_ocupacional',
            'centro_trabajo', 'contacto', 'relacion_empresa',
            'ponencia', 'ficha_tecnica', 'avales', 'presentacion'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'carne_identidad': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'categoria_ocupacional': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'centro_trabajo': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'relacion_empresa': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'carne_identidad': 'Carné de Identidad',
            'categoria_ocupacional': 'Categoría Ocupacional',
            'centro_trabajo': 'Centro de Trabajo',
            'contacto': 'Contacto (email/teléfono)',
            'relacion_empresa': 'Relación con la Empresa',
        }

    def clean_ponencia(self):
        ponencia = self.cleaned_data.get('ponencia')
        if ponencia:
            if ponencia.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError('El archivo de ponencia no puede ser mayor a 10MB.')
            if not ponencia.name.endswith('.pdf'):
                raise ValidationError('Solo se permiten archivos PDF para la ponencia.')
        return ponencia

    def clean_ficha_tecnica(self):
        ficha_tecnica = self.cleaned_data.get('ficha_tecnica')
        if ficha_tecnica:
            if ficha_tecnica.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('El archivo de ficha técnica no puede ser mayor a 5MB.')
            if not ficha_tecnica.name.endswith('.pdf'):
                raise ValidationError('Solo se permiten archivos PDF para la ficha técnica.')
        return ficha_tecnica

    def clean_avales(self):
        avales = self.cleaned_data.get('avales')
        if avales:
            if avales.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('El archivo de avales no puede ser mayor a 5MB.')
            if not avales.name.endswith('.pdf'):
                raise ValidationError('Solo se permiten archivos PDF para los avales.')
        return avales

    def clean_presentacion(self):
        presentacion = self.cleaned_data.get('presentacion')
        if presentacion:
            if presentacion.size > 20 * 1024 * 1024:  # 20MB
                raise ValidationError('El archivo de presentación no puede ser mayor a 20MB.')
            if not (presentacion.name.endswith('.ppt') or presentacion.name.endswith('.pptx')):
                raise ValidationError('Solo se permiten archivos PowerPoint para la presentación.')
        return presentacion

    def clean_carne_identidad(self):
        carne_identidad = self.cleaned_data.get('carne_identidad')
        if ParticipanteForum.objects.filter(carne_identidad=carne_identidad).exists():
            raise ValidationError('Este carné de identidad ya está registrado.')
        return carne_identidad


class ConfiguracionCorreoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionCorreo
        fields = ['email', 'activo']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'email': 'Correo electrónico para notificaciones',
            'activo': 'Activar este correo'
        }

class BancoProblemaForm(forms.ModelForm):
    class Meta:
        model = BancoProblema
        fields = ['año', 'numero', 'objetivo', 'problema', 'ponencia_consultar', 'prioridad', 'resuelto']
        widgets = {
            'año': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'max': '2030'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'problema': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ponencia_consultar': forms.TextInput(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'resuelto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'ponencia_consultar': 'Ponencia a consultar',
        }