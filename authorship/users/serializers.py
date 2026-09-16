from rest_framework import serializers
from .models import User, Notification
import bleach

def clean_plain_text(value):
    if value and isinstance(value, str):
        return bleach.clean(value.strip(), tags=[], attributes={}, strip=True)
    
    return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'biography', 'interests', 'first_name', 'last_name']
        
        extra_kwargs = {
            'password': {'write_only': True},
            'biography': {'required': False, 'allow_blank': True},
            'interests': {'required': False, 'allow_blank': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_first_name(self, value):
        return clean_plain_text(value)

    def validate_last_name(self, value):
        return clean_plain_text(value)

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