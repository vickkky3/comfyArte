from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Notification
import bleach

def clean_plain_text(value):
    if value and isinstance(value, str):
        return bleach.clean(value.strip(), tags=[], attributes={}, strip=True)
    
    return value

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="El nombre de usuario ya está en uso. Por favor, elige otro."
            )
        ],
        error_messages={
            'blank': 'El nombre de usuario no puede estar vacío.',
            'required': 'El nombre de usuario es obligatorio.'
        }
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'biography', 'interests', 'first_name', 'last_name']
        
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'blank': 'La contraseña no puede estar vacía.',
                    'required': 'La contraseña es obligatoria.'
                }
            },
            'first_name': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'blank': 'El nombre no puede estar vacío.',
                    'required': 'El nombre es obligatorio.'
                }
            },
            'last_name': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'blank': 'Los apellidos no pueden estar vacíos.',
                    'required': 'Los apellidos son obligatorios.'
                }
            },
            'email': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'blank': 'El correo electrónico no puede estar vacío.',
                    'required': 'El correo electrónico es obligatorio.'
                }
            },
            'biography': {'required': False, 'allow_blank': True},
            'interests': {'required': False, 'allow_blank': True},
        }

    def validate_first_name(self, value):
        cleaned = clean_plain_text(value)
        
        if not cleaned:
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        
        return cleaned

    def validate_last_name(self, value):
        cleaned = clean_plain_text(value)
        
        if not cleaned:
            raise serializers.ValidationError("Los apellidos no pueden estar vacíos.")
        
        return cleaned
    
    def validate_username(self, value):
        cleaned = clean_plain_text(value)
        
        if not cleaned:
            raise serializers.ValidationError("El nombre de usuario no puede estar vacío.")
        
        if " " in cleaned:
            raise serializers.ValidationError("El nombre de usuario no puede contener espacios.")
        
        query = User.objects.filter(username=cleaned)
        
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
            
        if query.exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso. Por favor, elige otro.")
        
        return cleaned

    def validate_email(self, value):
        cleaned = clean_plain_text(value).lower()
        if not cleaned:
            raise serializers.ValidationError("El correo electrónico no puede estar vacío.")
        
        try:
            django_validate_email(cleaned)
            
        except DjangoValidationError:
            raise serializers.ValidationError("Introduce un formato de correo electrónico válido.")
        
        return cleaned

    def validate_interests(self, value):
        return clean_plain_text(value)

    def validate_biography(self, value):
        return clean_plain_text(value)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        
        return user

class AuthorPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'biography', 'role']
        
class NotificationSerializer(serializers.ModelSerializer):
    work_title = serializers.CharField(source='work.title', read_only=True, default=None)
    author_username = serializers.CharField(source='work.author.username', read_only=True, default=None)
    sender_username = serializers.CharField(source='sender.username', read_only=True, default=None)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'sender',
            'sender_username',
            'work',
            'work_title',
            'author_username',
            'notification_type',
            'message',
            'created_at',
        ]