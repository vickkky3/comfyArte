from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

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