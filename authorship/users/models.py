from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('author', 'Autor'),
        ('consumer', 'Consumidor'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='consumer')
    biography = models.TextField(blank=True)
    interests = models.CharField(max_length=200, blank=True)
    
    public_key = models.TextField(blank=True, null=True)
    private_key = models.TextField(blank=True, null=True)

class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_work', 'Nueva obra publicada'),
        ('new_follower', 'Nuevo suscriptor / seguidor'),
        ('new_saved_work', 'Nueva obra guardada'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    
    work = models.ForeignKey(
        'works.Work', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=30, 
        choices=TYPE_CHOICES, 
        default='new_work'
    )
    
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificación ({self.notification_type}) para {self.recipient.username}"
    
           
@receiver(post_save, sender=User)
def generate_user_rsa_keys(sender, instance, created, **kwargs):
    if created:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
    
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        instance.private_key = private_pem
        instance.public_key = public_pem
        instance.save()