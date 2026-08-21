from rest_framework import serializers
from .models import User, Notification

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

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AuthorPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'biography', 'role']
        
class NotificationSerializer(serializers.ModelSerializer):
    work_title = serializers.CharField(source='work.title', read_only=True)
    author_username = serializers.CharField(source='work.author.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'work', 'work_title', 'author_username', 'message', 'created_at']