from django.db import models
from django.conf import settings
from subscriptions.models import SubscriptionPlan

class Work(models.Model):
    """Model representing a work of the platform."""
    TYPE_CHOICES = [
        ('book', 'Libro'),
        ('music', 'Música'),
        ('video', 'Vídeo'),
        ('software', 'Software'),
        ('paint', 'Pintura'),
        ('sculpture', 'Escultura'),
    ]
    
    LICENSES_CHOICES = [
        ('by', 'BY'),
        ('by-sa', 'BY-SA'),
        ('by-nd', 'BY-ND'),
        ('by-nc', 'BY-NC'),
        ('by-nc-sa', 'BY-NC-SA'),
        ('by-nc-nd', 'BY-NC-ND'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description=models.TextField(verbose_name="Descripción")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Autor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creando el")
    work_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='book', verbose_name="Tipo de obra")
    license = models.CharField(max_length=50, choices=LICENSES_CHOICES, default='by', verbose_name="Licencia")
    
    binary_file = models.BinaryField(blank=True, null=True, verbose_name="Obra original")
    file_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre fichero obra original")
    file_type = models.CharField(max_length=120, blank=True, verbose_name="Tipo fichero obra original")
    resume_file = models.BinaryField(blank=True, null=True, verbose_name="Muestra gratuita")
    resume_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre fichero muestra gratuita")
    resume_type = models.CharField(max_length=120, blank=True, verbose_name="Tipo fichero muestra gratuita")
    
    plan_required = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='works',
        verbose_name="Plan mínimo requerido"
    ) 
    
    hash_security = models.CharField(max_length=512, blank=True, null=True, verbose_name="Hash de la obra")
    
    STATUS_CHOICES = [
        ('approved', 'Aprobada'),
        ('appealed', 'Revisión manual solicitada'),
        ('rejected_manual', 'Rechazada definitivamente'),
        ('published', 'Publicada'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_ai',
        verbose_name="Estado de validación"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo de rechazo (IA o Manual)"
    )
    
    class Meta:
        permissions = [
            ("validate_work", "Can validate or reject works"),
            ("generate_hash", "Can generate authorship hash"),
            ("view_all_works", "Can view all works"),
        ]
        
        verbose_name = 'Obra'
        verbose_name_plural = 'Obras'
        
    def get_work_type(self):
        if hasattr(self, 'book'): return 'book'
        if hasattr(self, 'music'): return 'music'
        if hasattr(self, 'video'): return 'video'
        if hasattr(self, 'software'): return 'software'
        if hasattr(self, 'paint'): return 'paint'
        if hasattr(self, 'sculpture'): return 'sculpture'
        return 'generic'
    
class Book(Work):
    pages = models.IntegerField(verbose_name="Páginas")
    isbn = models.CharField(max_length=30, verbose_name="ISBN")
    genre = models.CharField(max_length=100, blank=True, verbose_name="Género")
    language = models.CharField(max_length=100, blank=True, verbose_name="Lenguaje")
    
    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'

class Music(Work):
    duration = models.FloatField(verbose_name="Duración")
    album = models.CharField(max_length=200, blank=True, verbose_name="Álbum")
    genre = models.CharField(max_length=100, blank=True, verbose_name="Género")
    
    class Meta:
        verbose_name = 'Música'
        verbose_name_plural = 'Música'
    
class Video(Work):
    duration = models.FloatField(verbose_name="Duración")
    genre = models.CharField(max_length=100, blank=True, verbose_name="Género")
    
    class Meta:
        verbose_name = 'Vídeo'
        verbose_name_plural = 'Vídeos'
    
class Software(Work):
    programming_language = models.CharField(max_length=50, verbose_name="Lenguaje de programación")
    repository_url = models.URLField(blank=True, null=True, verbose_name="Url repositorio del proyecto")
    documentation_url = models.URLField(blank=True,  null=True, verbose_name="Url repositorio de la documentación")
    
    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Software'
    
class Paint(Work):
    height = models.FloatField(verbose_name="Altura")
    weight = models.FloatField(verbose_name="Peso")
    PAINT_TYPES = (
        ('oil', 'Óleo'),
        ('acrylic', 'Acrílico'),
        ('watercolor', 'Acuarela'),
        ('digital', 'Digital'),
    )
    type = models.CharField(max_length=20, choices=PAINT_TYPES, verbose_name="Tipo")
    
    class Meta:
        verbose_name = 'Pintura'
        verbose_name_plural = 'Pinturas'
    
class Sculpture(Work):
    height = models.FloatField(verbose_name="Altura")
    weight = models.FloatField(verbose_name="Peso")
    SCULPTURE_TYPES = (
    ('marble', 'Mármol'),
        ('bronze', 'Bronce'),
        ('wood', 'Madera'),
        ('clay', 'Arcilla'),
    )
    type = models.CharField(max_length=20, choices=SCULPTURE_TYPES, verbose_name="Tipo")
    
    class Meta:
        verbose_name = 'Escultura'
        verbose_name_plural = 'Esculturas'


