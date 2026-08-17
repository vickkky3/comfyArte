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
        ('none', 'Sin licencia'),
        ('by', 'BY'),
        ('by-sa', 'BY-SA'),
        ('by-nd', 'BY-ND'),
        ('by-nc', 'BY-NC'),
        ('by-nc-sa', 'BY-NC-SA'),
        ('by-nc-nd', 'BY-NC-ND'),
    ]
    
    title = models.CharField(max_length=200)
    description=models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    work_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='book')
    license = models.CharField(max_length=20, choices=LICENSES_CHOICES, default='by')
    
    binary_file = models.BinaryField(blank=True, null=True)
    file_name = models.CharField(max_length=200, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    resume_file = models.BinaryField(blank=True, null=True)
    resume_name = models.CharField(max_length=200, blank=True)
    resume_type = models.CharField(max_length=50, blank=True)
    
    plan_required = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='works'
    ) 
    
    hash_security = models.CharField(max_length=64, blank=True, null=True)
    
    class Meta:
        permissions = [
            ("validate_work", "Can validate or reject works"),
            ("generate_hash", "Can generate authorship hash"),
            ("view_all_works", "Can view all works"),
        ]
        
    def get_work_type(self):
        if hasattr(self, 'book'): return 'book'
        if hasattr(self, 'music'): return 'music'
        if hasattr(self, 'video'): return 'video'
        if hasattr(self, 'software'): return 'software'
        if hasattr(self, 'paint'): return 'paint'
        if hasattr(self, 'sculpture'): return 'sculpture'
        return 'generic'
    
class Book(Work):
    pages = models.IntegerField()
    isbn = models.CharField(max_length=20)
    genre = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)

class Music(Work):
    duration = models.FloatField()
    album = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    
class Video(Work):
    duration = models.FloatField()
    genre = models.CharField(max_length=100, blank=True)
    
class Software(Work):
    programming_language = models.CharField(max_length=50)
    repository_url = models.URLField(blank=True, null=True)
    documentation_url = models.URLField(blank=True,  null=True)
    
class Paint(Work):
    height = models.FloatField()
    weight = models.FloatField()
    PAINT_TYPES = (
        ('oil', 'Óleo'),
        ('acrylic', 'Acrílico'),
        ('watercolor', 'Acuarela'),
        ('digital', 'Digital'),
    )
    type = models.CharField(max_length=20, choices=PAINT_TYPES)
    
class Sculpture(Work):
    height = models.FloatField()
    weight = models.FloatField()
    SCULPTURE_TYPES = (
    ('marble', 'Mármol'),
        ('bronze', 'Bronce'),
        ('wood', 'Madera'),
        ('clay', 'Arcilla'),
    )
    type = models.CharField(max_length=20, choices=SCULPTURE_TYPES)


