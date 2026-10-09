from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from .serializers import UserSerializer, AuthorPublicSerializer, NotificationSerializer
from .models import User, Notification

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        is_author = user.groups.filter(name="Author").exists()
        role = "Author" if is_author else "Consumer"

        return Response({
            'token': token.key,
            'role': role,
            'username': user.username
        })

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            raw_role = request.data.get('role', 'consumer')
            type_rol = str(raw_role).strip().lower()
            
            is_author = (type_rol == 'author')
            group_name = 'Author' if is_author else 'Consumer'
            
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            
            if hasattr(user, 'role'):
                user.role = group_name.lower()
                user.save()
            
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'role': group_name,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDataAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            user_obj = get_object_or_404(User, pk=pk)
            
        else:
            user_obj = request.user
            
        serializer = UserSerializer(user_obj)
        data = serializer.data
        
        data['es_autor'] = user_obj.groups.filter(name="Author").exists()
        data['es_consumidor'] = user_obj.groups.filter(name="Consumer").exists()
        
        return Response(data)
    
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):        
        queryset = User.objects.filter(role="author")
            
        serializer = AuthorPublicSerializer(queryset, many=True)
        return Response(serializer.data)
    
class NotificationsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):        
        queryset = Notification.objects.filter(recipient=request.user)
            
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)