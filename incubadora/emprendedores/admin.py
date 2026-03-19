# admin.py
from django.contrib import admin
from .models import Proyecto, Tutor
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from .models import Proyecto, Tutor, SesionMentoria, Tarea

# Ocultar grupos y usuarios predeterminados
admin.site.unregister(Group)
admin.site.unregister(User)

class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre_proyecto', 'usuario', 'estado', 'sector', 'fecha_registro')
    list_filter = ('estado', 'sector')
    search_fields = ('nombre_proyecto', 'nombre_completo', 'email')
    readonly_fields = ('fecha_registro',)
    list_editable = ('estado',)
    date_hierarchy = 'fecha_registro'
    
    # Acciones personalizadas
    actions = ['eliminar_seleccionados']
    
    def eliminar_seleccionados(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} proyectos eliminados correctamente")
    eliminar_seleccionados.short_description = "Eliminar proyectos seleccionados"

class TutorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'grado_academico', 'institucion', 'proyectos_actuales')
    search_fields = ('usuario__username', 'especialidades', 'usuario__first_name', 'usuario__last_name', 'usuario__email')
    list_filter = ('grado_academico', 'institucion')
    # Eliminar esta línea: filter_horizontal = ('proyectos_asignados',)
    
    def proyectos_actuales(self, obj):
        return obj.proyectos_asignados.count()
    proyectos_actuales.short_description = 'Proyectos'
    
    def nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    nombre_completo.short_description = 'Nombre'
    
    def email(self, obj):
        return obj.usuario.email
    email.short_description = 'Correo'
    
    # Acciones personalizadas
    actions = ['eliminar_seleccionados']
    
    def eliminar_seleccionados(self, request, queryset):
        for tutor in queryset:
            usuario = tutor.usuario
            tutor.delete()
            usuario.delete()
        count = queryset.count()
        self.message_user(request, f"{count} tutores eliminados correctamente")
    eliminar_seleccionados.short_description = "Eliminar tutores seleccionados"

# Modelo personalizado para emprendedores
class EmprendedorAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'proyectos_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    actions = ['eliminar_seleccionados']
    
    def proyectos_count(self, obj):
        return obj.proyectos.count()
    proyectos_count.short_description = 'Proyectos'
    
    def eliminar_seleccionados(self, request, queryset):
        count = queryset.count()
        for user in queryset:
            user.delete()
        self.message_user(request, f"{count} usuarios eliminados correctamente")
    eliminar_seleccionados.short_description = "Eliminar usuarios seleccionados"
    
    # Solo mostrar emprendedores
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_superuser=False)

# Registrar modelos personalizados
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Tutor, TutorAdmin)
admin.site.register(User, EmprendedorAdmin)
admin.site.register(SesionMentoria)
admin.site.register(Tarea)

# Personalizar títulos del admin
admin.site.site_header = "Incubadora Desoft - Administración"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Gestión de Incubación"

from .models import ParticipanteForum, ConfiguracionCorreo

@admin.register(ParticipanteForum)
class ParticipanteForumAdmin(admin.ModelAdmin):
    list_display = ('numero_expediente', 'nombre_completo', 'carne_identidad', 'centro_trabajo', 'fecha_inscripcion', 'evaluado', 'aceptado')
    list_filter = ('evaluado', 'aceptado', 'categoria_ocupacional', 'relacion_empresa')
    search_fields = ('numero_expediente', 'nombre_completo', 'carne_identidad', 'centro_trabajo')
    readonly_fields = ('fecha_inscripcion', 'numero_expediente')
    list_per_page = 20

@admin.register(ConfiguracionCorreo)
class ConfiguracionCorreoAdmin(admin.ModelAdmin):
    list_display = ('email', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('email',)
    readonly_fields = ('fecha_creacion',)