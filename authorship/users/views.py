from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from .serializers import UserSerializer, AuthorPublicSerializer

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            type_rol = request.data.get('role', 'consumer')
            user.role = type_rol
            user.save()

            group_name = 'Author' if type_rol == 'author' else 'Consumer'
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                print(f"Error: El grupo {group_name} no existe en la base de datos")
            
            token, _ = Token.objects.get_or_create(user=user)
            
            response_data = serializer.data
            response_data['token'] = token.key
            response_data['role'] = user.role
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDataAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data
        data['es_autor'] = request.user.groups.filter(name="Author").exists()
        data['es_consumidor'] = request.user.groups.filter(name="Consumer").exists()
        return Response(data)
    
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()

class AuthorListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):        
        queryset = User.objects.filter(role="author")
            
        serializer = AuthorPublicSerializer(queryset, many=True)
        return Response(serializer.data)