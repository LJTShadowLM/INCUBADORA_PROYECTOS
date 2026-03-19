# management/commands/enviar_recordatorios.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from emprendedores.models import SesionMentoria

class Command(BaseCommand):
    help = 'Envía recordatorios de sesiones de mentoría'

    def handle(self, *args, **options):
        ahora = timezone.now()
        
        # Recordatorios 24 horas antes
        recordatorios_24h = SesionMentoria.objects.filter(
            estado='confirmada',
            fecha_propuesta__range=(ahora + timedelta(hours=23), ahora + timedelta(hours=25))
        )
        
        for sesion in recordatorios_24h:
            self.enviar_recordatorio(sesion, '24h')
        
        # Recordatorios 1 hora antes
        recordatorios_1h = SesionMentoria.objects.filter(
            estado='confirmada',
            fecha_propuesta__range=(ahora + timedelta(minutes=55), ahora + timedelta(minutes=65))
        )
        
        for sesion in recordatorios_1h:
            self.enviar_recordatorio(sesion, '1h')
        
        # Verificar materiales faltantes (48 horas antes)
        verificacion_materiales = SesionMentoria.objects.filter(
            estado='confirmada',
            fecha_propuesta__range=(ahora + timedelta(hours=47), ahora + timedelta(hours=49)),
            es_material_obligatorio=True
        ).exclude(archivos__isnull=False)
        
        for sesion in verificacion_materiales:
            self.enviar_alerta_materiales(sesion)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Procesados: {len(recordatorios_24h)} recordatorios 24h, '
                f'{len(recordatorios_1h)} recordatorios 1h, '
                f'{len(verificacion_materiales)} alertas de materiales'
            )
        )
    
    def enviar_recordatorio(self, sesion, tipo):
        # Determinar destinatarios
        destinatarios = [sesion.proyecto.usuario.email, sesion.creada_por.email]
        
        # Renderizar email
        contexto = {'sesion': sesion, 'tipo': tipo}
        asunto = f"Recordatorio de sesión: {sesion.proyecto.nombre_proyecto}"
        contenido = render_to_string('emails/recordatorio_sesion.html', contexto)
        
        # Enviar email
        try:
            send_mail(
                asunto,
                '',
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
                html_message=contenido,
                fail_silently=False
            )
            self.stdout.write(f"Recordatorio {tipo} enviado para sesión {sesion.id}")
        except Exception as e:
            self.stderr.write(f"Error enviando recordatorio {tipo} para sesión {sesion.id}: {e}")
    
    def enviar_alerta_materiales(self, sesion):
        # Enviar alerta solo al emprendedor
        contexto = {'sesion': sesion}
        asunto = f"Materiales pendientes para sesión: {sesion.proyecto.nombre_proyecto}"
        contenido = render_to_string('emails/alerta_materiales.html', contexto)
        
        try:
            send_mail(
                asunto,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [sesion.proyecto.usuario.email],
                html_message=contenido,
                fail_silently=False
            )
            self.stdout.write(f"Alerta de materiales enviada para sesión {sesion.id}")
        except Exception as e:
            self.stderr.write(f"Error enviando alerta de materiales para sesión {sesion.id}: {e}")