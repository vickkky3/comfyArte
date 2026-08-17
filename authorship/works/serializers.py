from rest_framework import serializers

from subscriptions.serializers import SubscriptionPlanSerializer
from .models import Work

class WorkSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    license = serializers.ChoiceField(choices=Work.LICENSES_CHOICES, required=False)
    binary_file = serializers.FileField(write_only=True, required=False)
    resume_file = serializers.FileField(write_only=True, required=False)
    plan_required = SubscriptionPlanSerializer(read_only=True)
    isbn = serializers.CharField(required=False, write_only=True)
    language = serializers.CharField(required=False, write_only=True)
    album = serializers.CharField(required=False, write_only=True)
    genre = serializers.CharField(required=False, write_only=True)
    pages = serializers.IntegerField(required=False, write_only=True)
    duration = serializers.FloatField(required=False, write_only=True)
    programming_language = serializers.CharField(required=False, write_only=True)
    repository_url = serializers.URLField(required=False, write_only=True)
    documentation_url = serializers.URLField(required=False, write_only=True)
    height = serializers.FloatField(required=False, write_only=True)
    weight = serializers.FloatField(required=False, write_only=True)
    type_detail = serializers.CharField(required=False, write_only=True)
    hash_security = serializers.CharField(required=False)
    
    class Meta:
        model = Work
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)            
        if instance.work_type == 'book' and hasattr(instance, 'book'):
            data['isbn'] = instance.book.isbn
            data['pages'] = instance.book.pages
            data['genre'] = instance.book.genre
            data['language'] = instance.book.language
            
        if instance.work_type == 'music' and hasattr(instance, 'music'):
            data['duration'] = instance.music.duration
            data['album'] = instance.music.album
            data['genre'] = instance.music.genre
            
        if instance.work_type == 'video' and hasattr(instance, 'video'):
            data['duration'] = instance.video.duration
            data['genre'] = instance.video.genre
            
        if instance.work_type == 'software' and hasattr(instance, 'software'):
            data['programming_language'] = instance.software.programming_language
            data['repository_url'] = instance.software.repository_url 
            data['documentation_url'] = instance.software.documentation_url 
            
        if instance.work_type == 'paint' and hasattr(instance, 'paint'):
            data['height'] = instance.paint.height
            data['weight'] = instance.paint.weight
            data['type_detail'] = instance.paint.get_type_display()
        
        if instance.work_type == 'sculpture' and hasattr(instance, 'sculpture'):
            data['height'] = instance.sculpture.height
            data['weight'] = instance.sculpture.weight
            data['type_detail'] = instance.sculpture.get_type_display()
    
        return data