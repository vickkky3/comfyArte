from rest_framework import serializers

from subscriptions.serializers import SubscriptionPlanSerializer
from .models import Book, Work, Paint, Music, Video, Sculpture
import bleach

def clean_plain_text(value):
    if value and isinstance(value, str):
        return bleach.clean(value.strip(), tags=[], attributes={}, strip=True)
    
    return value

class WorkSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    license = serializers.ChoiceField(choices=Work.LICENSES_CHOICES, required=True)
    plan_required = SubscriptionPlanSerializer(read_only=True)
    
    binary_file = serializers.FileField(write_only=True, required=False)
    resume_file = serializers.FileField(write_only=True, required=False)
    
    isbn = serializers.CharField(required=False, write_only=True)
    language = serializers.ChoiceField(choices=Book.LANGUAGE_CHOICES, required=False, write_only=True)
    genre = serializers.ChoiceField(choices=Book.GENRE_CHOICES, required=False, write_only=True)
    pages = serializers.IntegerField(required=False, write_only=True)
    
    duration = serializers.FloatField(required=False, write_only=True)
    album = serializers.CharField(required=False, write_only=True)
    music_genre = serializers.ChoiceField(choices=Music.GENRE_CHOICES, required=False, write_only=True)
    
    video_genre = serializers.ChoiceField(choices=Video.GENRE_CHOICES, required=False, write_only=True)
    
    programming_language = serializers.CharField(required=False, write_only=True)
    repository_url = serializers.URLField(required=False, write_only=True)
    documentation_url = serializers.URLField(required=False, write_only=True)
    
    height = serializers.FloatField(required=False, write_only=True)
    weight = serializers.FloatField(required=False, write_only=True)
    paint_type = serializers.ChoiceField(choices=Paint.PAINT_TYPES, required=False, write_only=True)
    sculpture_type = serializers.ChoiceField(choices=Sculpture.SCULPTURE_TYPES, required=False, write_only=True)
    
    type_detail = serializers.CharField(required=False, write_only=True)
    hash_security = serializers.CharField(required=False)
    
    class Meta:
        model = Work
        fields = '__all__'
        read_only_fields = (
            'file_name',
            'file_type',
            'resume_name',
            'resume_type',
            'hash_security',
            'status',
            'rejection_reason'
        )
        
        extra_kwargs = {
            'binary_file': {'write_only': True},
            'resume_file': {'write_only': True},
            'title': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'blank': 'El ttítulo no puede estar vacío.',
                    'required': 'El título es obligatorio.'
                }
            },
            'description': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'blank': 'La descripción no puede estar vacía.',
                    'required': 'La descripción es obligatoria.'
                }
            },
        }
        
    def validate_title(self, value):
        return clean_plain_text(value)

    def validate_description(self, value):
        return clean_plain_text(value)

    def validate_isbn(self, value):
        return clean_plain_text(value)

    def validate_album(self, value):
        return clean_plain_text(value)

    def validate_repository_url(self, value):
        return clean_plain_text(value)
    
    def validate_documentation_url(self, value):
        return clean_plain_text(value)

    def validate_programming_language(self, value):
        return clean_plain_text(value)
    
    def validate(self, attrs):
        errors = {}


        work_type = attrs.get('work_type') or (self.instance.work_type if self.instance else None)

        if work_type == 'book':
            if not attrs.get('pages') and not (self.instance and hasattr(self.instance, 'book') and self.instance.book.pages):
                errors['pages'] = ['El número de páginas es obligatorio para los libros.']
                
            if not attrs.get('genre') and not (self.instance and hasattr(self.instance, 'book') and self.instance.book.genre):
                errors['genre'] = ['El género es obligatorio para los libros.']
                
            if not attrs.get('language') and not (self.instance and hasattr(self.instance, 'book') and self.instance.book.language):
                errors['language'] = ['El idioma es obligatorio para los libros.']

        elif work_type == 'music':
            if not attrs.get('duration') and not (self.instance and hasattr(self.instance, 'music') and self.instance.music.duration):
                errors['duration'] = ['La duración es obligatoria para las pistas de música.'] 
                
            if not attrs.get('music_genre') and not (self.instance and hasattr(self.instance, 'music') and self.instance.music.genre):
                errors['music_genre'] = ['El género es obligatorio para las pistas de música.']

        elif work_type == 'video':
            if not attrs.get('duration') and not (self.instance and hasattr(self.instance, 'video') and self.instance.video.duration):
                errors['duration'] = ['La duración es obligatoria para los vídeos.']
                
            if not attrs.get('video_genre') and not (self.instance and hasattr(self.instance, 'video') and self.instance.video.genre):
                errors['video_genre'] = ['El género es obligatorio para los vídeos.']

        elif work_type == 'software':
            if not attrs.get('programming_language') and not (self.instance and hasattr(self.instance, 'software') and self.instance.software.programming_language):
                errors['programming_language'] = ['El lenguaje de programación es obligatorio.']

        elif work_type == 'paint':
            paint_type_val = attrs.get('paint_type')
            has_existing = self.instance and hasattr(self.instance, 'paint') and self.instance.paint.type

            if not paint_type_val and not has_existing:
                errors['paint_type'] = ['La técnica de pintura es obligatoria.']

        elif work_type == 'sculpture':
            sculpture_type_val = attrs.get('sculpture_type')
            has_existing = self.instance and hasattr(self.instance, 'sculpture') and self.instance.sculpture.type

            if not sculpture_type_val and not has_existing:
                errors['sculpture_type'] = ['El material de la escultura es obligatorio.']

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)     
               
        if instance.work_type == 'book' and hasattr(instance, 'book'):
            data['isbn'] = instance.book.isbn
            data['pages'] = instance.book.pages
            data['genre'] = instance.book.get_genre_display()
            data['language'] = instance.book.get_language_display()
            
        if instance.work_type == 'music' and hasattr(instance, 'music'):
            data['duration'] = instance.music.duration
            data['album'] = instance.music.album
            data['music_genre'] = instance.music.get_genre_display()
            
        if instance.work_type == 'video' and hasattr(instance, 'video'):
            data['duration'] = instance.video.duration
            data['video_genre'] = instance.video.get_genre_display()
            
        if instance.work_type == 'software' and hasattr(instance, 'software'):
            data['programming_language'] = instance.software.programming_language
            data['repository_url'] = instance.software.repository_url 
            data['documentation_url'] = instance.software.documentation_url 
            
        if instance.work_type == 'paint' and hasattr(instance, 'paint'):
            data['height'] = instance.paint.height
            data['weight'] = instance.paint.weight
            data['paint_type'] = instance.paint.get_type_display()
        
        if instance.work_type == 'sculpture' and hasattr(instance, 'sculpture'):
            data['height'] = instance.sculpture.height
            data['weight'] = instance.sculpture.weight
            data['sculpture_type'] = instance.sculpture.get_type_display()
    
        return data