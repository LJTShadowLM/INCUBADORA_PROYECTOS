from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro_proyecto, name='registro'),
    path('registro-exito/', views.registro_exito, name='registro_exito'),
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    
    # Autenticación
    path('registro/<str:tipo_usuario>/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Paneles
    path('panel/', views.panel_usuario, name='panel_usuario'),
    path('panel/admin/', views.panel_admin, name='panel_admin'),
    path('panel/gestor/', views.panel_gestor, name='panel_gestor'),
    path('panel/emprendedor/', views.panel_emprendedor, name='panel_emprendedor'),
    
    # Acciones 
    path('proyecto/<int:proyecto_id>/cambiar-estado/<str:nuevo_estado>/', 
         views.cambiar_estado_proyecto_gestor, name='cambiar_estado'),
    path('proyecto/<int:proyecto_id>/asignar-gestor/', 
         views.asignar_gestor, name='asignar_gestor'),
    path('panel/admin/registrar-gestor/', 
         views.registrar_gestor, name='registrar_gestor'),
    
    # Nuevas URLs para administrador (gestor)
    path('panel/admin/gestor/<int:gestor_id>/eliminar/', 
         views.eliminar_gestor, name='eliminar_gestor'),
    path('panel/admin/gestor/<int:gestor_id>/editar/', 
         views.editar_gestor, name='editar_gestor'),
    path('panel/admin/emprendedor/<int:emprendedor_id>/asignar-gestor/', 
         views.asignar_gestor_emprendedor, name='asignar_gestor_emprendedor'),

    path('panel/emprendedor/agregar-proyecto/', views.agregar_proyecto, name='agregar_proyecto'),
    path('panel/emprendedor/bandeja/', views.bandeja_emprendedor, name='bandeja_emprendedor'),
    
    # Nuevas URLs para gestor 
    path('tareas/<int:tarea_id>/completar/', views.completar_tarea_ajax, name='completar_tarea_ajax'),
    path('enviar-mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('agendar-evento/', views.agendar_evento, name='agendar_evento'),
    path('cambiar-estado-proyecto/<int:proyecto_id>/', views.cambiar_estado_proyecto_gestor, name='cambiar_estado_proyecto_gestor'),
    path('rechazar-proyecto/<int:proyecto_id>/', views.rechazar_proyecto, name='rechazar_proyecto'),

    # URLs para sesiones de mentoría
    path('sesiones/crear/<int:proyecto_id>/', views.crear_sesion_mentoria, name='crear_sesion'),
    path('sesiones/<int:sesion_id>/', views.detalle_sesion, name='detalle_sesion'),
    path('sesiones/<int:sesion_id>/responder/', views.responder_sesion, name='responder_sesion'),
    path('sesiones/<int:sesion_id>/proponer-horarios/', views.proponer_horarios, name='proponer_horarios'),
    path('sesiones/propuesta/<int:propuesta_id>/aceptar/', views.aceptar_propuesta_horario, name='aceptar_propuesta_horario'),
    path('sesiones/<int:sesion_id>/subir-archivo/', views.subir_archivo_sesion, name='subir_archivo_sesion'),
    path('sesiones/<int:sesion_id>/marcar-realizada/', views.marcar_sesion_realizada, name='marcar_sesion_realizada'),
    path('proyecto/<int:proyecto_id>/sesiones/', views.listar_sesiones_proyecto, name='listar_sesiones_proyecto'),
    path('panel/admin/gestor/<int:gestor_id>/ver/', views.ver_gestor, name='ver_gestor'),
    path('panel/admin/emprendedor/<int:emprendedor_id>/ver/', views.ver_emprendedor, name='ver_emprendedor'),
    path('proyecto/<int:proyecto_id>/solicitar-sesion/', views.solicitar_sesion_emprendedor, name='solicitar_sesion_emprendedor'),
    
    # URLs para mensajes
    path('mensajes/', views.ver_mensajes, name='ver_mensajes'),
    path('mensajes/<int:mensaje_id>/marcar-leido/', views.marcar_mensaje_leido, name='marcar_mensaje_leido'),
    path('enviar-mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
   
    # URLs para el Forum Evento (sin cambios)
    path('forum-eventos/', views.forum_evento, name='forum_evento'),
    path('forum-eventos/convocatoria/', views.ver_convocatoria, name='ver_convocatoria'),
    path('forum-eventos/gestion-convocatoria/', views.gestion_convocatoria, name='gestion_convocatoria'),
    path('forum-eventos/editar-convocatoria/<int:convocatoria_id>/', views.editar_convocatoria, name='editar_convocatoria'),
    path('forum-eventos/gestion-categorias/<int:convocatoria_id>/', views.gestion_categorias, name='gestion_categorias'),
    path('forum-eventos/gestion-documentos/', views.gestion_documentos, name='gestion_documentos'),
    path('forum-eventos/programa/', views.programa_forum, name='programa_forum'),
    path('forum-eventos/comision-forum/', views.comision_forum, name='comision_forum'),
    path('forum-eventos/comite-organizador/', views.comite_organizador, name='comite_organizador'),
    path('forum-eventos/comision/agregar-miembro/', views.agregar_miembro, name='agregar_miembro'),
    path('forum-eventos/comision/editar-miembro/<int:miembro_id>/', views.editar_miembro, name='editar_miembro'),
    path('forum-eventos/comision/eliminar-miembro/<int:miembro_id>/', views.eliminar_miembro, name='eliminar_miembro'),
    path('forum-eventos/comision/agregar-comision/', views.agregar_comision, name='agregar_comision'),
    path('forum-eventos/comision/editar-comision/<int:comision_id>/', views.editar_comision, name='editar_comision'),
    path('forum-eventos/programa/agregar/', views.agregar_actividad_programa, name='agregar_actividad_programa'),
    path('forum-eventos/programa/editar/<int:actividad_id>/', views.editar_actividad_programa, name='editar_actividad_programa'),
    path('forum-eventos/programa/eliminar/<int:actividad_id>/', views.eliminar_actividad_programa, name='eliminar_actividad_programa'),
    path('forum-eventos/comision/eliminar-comision/<int:comision_id>/', views.eliminar_comision, name='eliminar_comision'),
    path('proyectos-finalizados/', views.proyectos_finalizados, name='proyectos_finalizados'),
    path('innovacion/', views.trabajos_innovacion, name='trabajos_innovacion'),
    path('innovacion/agregar/', views.agregar_trabajo_innovacion, name='agregar_trabajo_innovacion'),
    path('innovacion/editar/<int:trabajo_id>/', views.editar_trabajo_innovacion, name='editar_trabajo_innovacion'),
    path('innovacion/eliminar/<int:trabajo_id>/', views.eliminar_trabajo_innovacion, name='eliminar_trabajo_innovacion'),
    path('resumen-innovacion/', views.resumen_innovacion, name='resumen_innovacion'),
    path('resumen-innovacion/agregar/', views.agregar_resumen_innovacion, name='agregar_resumen_innovacion'),
    path('resumen-innovacion/editar/<int:resumen_id>/', views.editar_resumen_innovacion, name='editar_resumen_innovacion'),
    path('resumen-innovacion/eliminar/<int:resumen_id>/', views.eliminar_resumen_innovacion, name='eliminar_resumen_innovacion'),
    path('forum/participar/', views.participar_forum, name='participar_forum'),
    path('forum/confirmacion/<str:numero_expediente>/', views.confirmacion_inscripcion, name='confirmacion_inscripcion'),
    path('forum/ver-estado/', views.ver_estado_inscripcion, name='ver_estado_inscripcion'),
    path('forum/gestionar-correo/', views.gestionar_correo, name='gestionar_correo'),
    path('forum/eliminar-configuracion/<int:configuracion_id>/', views.eliminar_configuracion_correo, name='eliminar_configuracion_correo'),
    path('forum/banco-problemas/', views.banco_problemas, name='banco_problemas'),
    # Banco de Problemas
    path('forum/banco-problemas/gestion/', views.gestionar_banco_problemas, name='gestionar_banco_problemas'),
    path('forum/banco-problemas/agregar/', views.agregar_problema, name='agregar_problema'),
    path('forum/banco-problemas/editar/<int:problema_id>/', views.editar_problema, name='editar_problema'),
    path('forum/banco-problemas/eliminar/<int:problema_id>/', views.eliminar_problema, name='eliminar_problema'),
   
    path('panel/admin/gestores/', views.lista_gestores, name='lista_gestores'),
    path('panel/admin/emprendedores/', views.lista_emprendedores, name='lista_emprendedores'),
    path('panel/admin/proyectos/', views.lista_proyectos, name='lista_proyectos'),
    
    path('panel/gestor/crear-tarea/', views.crear_tarea_gestor, name='crear_tarea_gestor'),
    path('panel/gestor/bandeja/', views.bandeja_gestor, name='bandeja_gestor'),
    
    #Ventanilla 
    path('ventanilla-unica/', views.ventanilla_unica, name='ventanilla_unica'),
    path('ventanilla-unica/solicitud/', views.enviar_solicitud_ventanilla, name='enviar_solicitud_ventanilla'),
    path('panel/emprendedor/bandeja/', views.bandeja_emprendedor, name='bandeja_emprendedor'),
    path('ventanilla-unica/solicitud/<int:solicitud_id>/gestionar/', views.gestionar_solicitud_ventanilla, name='gestionar_solicitud_ventanilla'),
]