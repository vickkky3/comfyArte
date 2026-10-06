from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('author', 'Autor'),
        ('consumer', 'Consumidor'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='consumer', verbose_name="Rol")
    biography = models.TextField(blank=True, verbose_name="Biografía")
    interests = models.CharField(max_length=200, blank=True, verbose_name="Intereses")
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def save(self, *args, **kwargs):
        if (self.is_superuser or self.is_staff) and self.role != 'admin':
            self.role = 'admin'
            
        super().save(*args, **kwargs)

class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_work', 'Nueva obra publicada'),
        ('new_follower', 'Nuevo suscriptor / seguidor'),
        ('new_saved_work', 'Nueva obra guardada'),
        ('approved_work', 'Obra aprobada por el administrador'),
        ('rejected_work', 'Obra rechazada por el administrador'),
        ('plan_expiring', 'Plan a punto de expirar'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatario'
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='Remitente'
    )
    
    work = models.ForeignKey(
        'works.Work', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='notifications',
        verbose_name='Obra'
    )
    
    notification_type = models.CharField(
        max_length=30, 
        choices=TYPE_CHOICES, 
        default='new_work',
        verbose_name='Tipo de notificación'
    )
    
    message = models.TextField(verbose_name='Mensaje')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"Notificación ({self.notification_type}) para {self.recipient.username}"
    