from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from subscriptions.models import SubscriptionPlan
from .models import Work
from users.models import Notification, User
from subscriptions.models import AuthorSubscription
from .serializers import WorkSerializer
from .models import Work, Book, Music, Video, Software, Paint, Sculpture
from rest_framework.parsers import MultiPartParser, FormParser
import base64
from .services import validate_work_content, process_file_for_ai
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

ALLOWED_EXTENSIONS = {
    'pdf', 'jpg', 'jpeg', 'png', 'webp', 
    
    'mp3', 'wav', 'ogg', 
    'mp4', 'avi', 'mov', 
    
    'zip',

    'py', 'js', 'ts', 'jsx', 'tsx', 'vue', 'html', 'css', 
    'java', 'c', 'cpp', 'cs', 'php', 'rb', 'go', 'rs', 
    'swift', 'kt', 'sql', 'sh', 'ipynb', 'json', 'xml', 'yaml', 'yml'
}

def is_extension_allowed(filename):
        if not filename or '.' not in filename:
            return False
        
        if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            return True
        
        return False

class WorkListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        user = request.user
        
        if user.groups.filter(name="Author").exists():
            queryset = Work.objects.filter(author=user)
        else:
            
            queryset = Work.objects.all()
            
        serializer = WorkSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data
        work_type = data.get('work_type')
        
        serializer = WorkSerializer(data=data)
        
        if not request.user.has_perm('works.add_work'):
            return Response(
                {"error": "Tu cuenta no tiene permisos para registrar nuevas obras en la plataforma."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if serializer.is_valid():
            try:
                models_map = {
                    'book': Book,
                    'music': Music,
                    'video': Video,
                    'software': Software,
                    'paint': Paint,
                    'sculpture': Sculpture
                }
                model_class = models_map.get(work_type, Work)
                
                valid_fields = {field.name for field in model_class._meta.get_fields()}
                
                create_data = {}
                for k, v in data.items():
                    if k != 'file_upload' and k != 'resume_upload' and v != "":
                        if k in valid_fields:
                            create_data[k] = v
                        
                plan_id = data.get('plan_required')
                
                if plan_id and plan_id != "":
                    plan_obj = SubscriptionPlan.objects.get(id=plan_id)
                    create_data['plan_required'] = plan_obj
                    
                else:
                    create_data['plan_required'] = None
                
                if work_type in ['paint', 'sculpture'] and 'type_detail' in create_data:
                    create_data['type'] = create_data.pop('type_detail')
                
                file = request.FILES.get('file_upload')
                resume = request.FILES.get('resume_upload')
                
                title = data.get('title')
                description = data.get('description')
                
                file_info = process_file_for_ai(file)
                resume_info = process_file_for_ai(resume)
                
                result_ai_validator = validate_work_content(title, description, file_info, resume_info)
                
                print("--- RESULTADO DE LA IA ---", result_ai_validator)
                
                if not result_ai_validator.get("is_valid"):
                    return Response(
                        {"error": f"La obra fue rechazada por el sistema de validación: {result_ai_validator.get('reason')}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if file:
                    
                    if not is_extension_allowed(file.name):
                        return Response(
                            {"error": "Formato de archivo no permitido. Los formatos aceptados son: .pdf, .jpg, .jpeg, .png, .webp, .mp3, .wav, .ogg, .mp4, .avi, .mov, .zip"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        

                    if resume and not is_extension_allowed(resume.name):
                        return Response(
                            {"error": "Formato del archivo de muestra no permitido."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
    
    
                    binary_file = file.read()
                    create_data['binary_file'] = binary_file
                    create_data['file_name'] = file.name
                    create_data['file_type'] = file.content_type
                    
                    user_private_key_pem = request.user.private_key
                
                    if not user_private_key_pem:
                        return Response({"error": "El usuario no dispone de una clave privada para firmar."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    private_key = serialization.load_pem_private_key(
                        user_private_key_pem.encode('utf-8'),
                        password=None
                    )   
                    
                    signature = private_key.sign(
                        binary_file,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    
                    signature_base64 = base64.b64encode(signature).decode('utf-8')
                    
                    create_data['hash_security'] = signature_base64
                    
                else:
                    return Response(
                        {"error": "Es obligatorio adjuntar un archivo para registrar y firmar la obra."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                if resume:
                    resume_file = resume.read()
                    create_data['resume_file'] = resume_file
                    create_data['resume_name'] = resume.name
                    create_data['resume_type'] = resume.content_type
                                    
                obj = model_class.objects.create(author=request.user, **create_data)
                
                subscriptions = AuthorSubscription.objects.filter(author=request.user)
                
                notifications_to_create = []
                for sub in subscriptions:
                    notifications_to_create.append(
                        Notification(
                            recipient=sub.consumer,
                            work=obj,
                            message=f"El autor {request.user.username} ha publicado una nueva obra: '{obj.title}'"
                        )
                    )
                    
                if notifications_to_create:
                    Notification.objects.bulk_create(notifications_to_create)

                return Response(WorkSerializer(obj).data, status=status.HTTP_201_CREATED)
                            
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class WorkDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        serializer = WorkSerializer(work)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        
        if(work.author != request.user):
            return Response(
            {"error": "No tienes permiso para eliminar esta obra."}, 
            status=status.HTTP_403_FORBIDDEN
        )
        
        work.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        
        if work.author != request.user:
            return Response(
                {"error": "No tienes autorización para modificar esta obra."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        work_type = data.get('work_type', work.work_type)
        
        serializer = WorkSerializer(work, data=data, partial=True)
        
        models_map = {
        'book': Book,
        'music': Music,
        'video': Video,
        'software': Software,
        'paint': Paint,
        'sculpture': Sculpture
        }
        
        model_class = models_map.get(work_type, Work)
        
        if serializer.is_valid():
            try:
                obj = model_class.objects.get(pk=work.pk)
                
                valid_fields = {field.name for field in model_class._meta.get_fields()}
                
                create_data = {}
                for k, v in data.items():
                    if k != 'file_upload' and k != 'resume_upload' and v != "":
                        if k in valid_fields:
                            create_data[k] = v
                        
                plan_id = data.get('plan_required')
                
                if plan_id and plan_id != "":
                    plan_obj = SubscriptionPlan.objects.get(id=plan_id)
                    create_data['plan_required'] = plan_obj
                    
                else:
                    create_data['plan_required'] = None
                
                if work_type in ['paint', 'sculpture'] and 'type_detail' in create_data:
                    create_data['type'] = create_data.pop('type_detail')
                
                file = request.FILES.get('file_upload')
                resume = request.FILES.get('resume_upload')
                
                if file:
                    binary_file = file.read()
                    create_data['binary_file'] = binary_file
                    create_data['file_name'] = file.name
                    create_data['file_type'] = file.content_type
                    
                    user_private_key_pem = request.user.private_key
                
                    if not user_private_key_pem:
                        return Response({"error": "El usuario no dispone de una clave privada para firmar."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    private_key = serialization.load_pem_private_key(
                        user_private_key_pem.encode('utf-8'),
                        password=None
                    )   
                    
                    signature = private_key.sign(
                        binary_file,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    
                    signature_base64 = base64.b64encode(signature).decode('utf-8')
                    
                    create_data['hash_security'] = signature_base64
                
                if resume:
                    resume_file = resume.read()
                    create_data['resume_file'] = resume_file
                    create_data['resume_name'] = resume.name
                    create_data['resume_type'] = resume.content_type
                    
                for key, value in create_data.items():
                    setattr(obj, key, value)
                    
                obj.save()
                    
                return Response(WorkSerializer(obj).data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ListWorksByAuthorAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id):
        queryset = Work.objects.filter(author_id=author_id)
        
        serializer = WorkSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
          
    
class ServeWorkFileAPIView(APIView):
    """
    Vista protegida para servir de forma segura el archivo binario 
    asociado a una obra registrada.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        
        if not work.binary_file:
            return Response(
                {"error": "Esta obra no tiene ningún archivo digital adjunto."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(work.binary_file, content_type=work.file_type)
        
        response['Content-Disposition'] = f'inline; filename="{work.file_name}"'
        
        return response
    
class ServeWorkResumeAPIView(APIView):
    """
    Vista elástica para servir la muestra gratuita / resumen 
    sin restricciones de suscripción comercial.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        
        if not work.resume_file:
            return HttpResponse("Esta obra no dispone de muestra gratuita.", status=404)
        
        response = HttpResponse(work.resume_file, content_type=work.resume_type)
        response['Content-Disposition'] = f'inline; filename="preview_{work.resume_name}"'
        return response