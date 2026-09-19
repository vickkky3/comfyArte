from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from pathlib import Path

from subscriptions.models import SubscriptionPlan
from .models import Work
from users.models import Notification
from subscriptions.models import AuthorSubscription
from .serializers import WorkSerializer
from .models import Work, Book, Music, Video, Software, Paint, Sculpture
from rest_framework.parsers import MultiPartParser, FormParser
import base64
from .services import validate_work_content, process_file_for_ai, get_recommended_authors_for_user
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from .throttles import CryptoOpsRateThrottle

ALLOWED_EXTENSIONS = {
    'pdf', 'txt', 'jpg', 'jpeg', 'png', 'webp', 
    
    'mp3', 'wav', 'ogg', 
    'mp4', 'avi', 'mov', 
    
    'zip',

    'py', 'js', 'ts', 'jsx', 'tsx', 'vue', 'html', 'css', 
    'java', 'c', 'cpp', 'cs', 'php', 'rb', 'go', 'rs', 
    'swift', 'kt', 'sql', 'sh', 'ipynb', 'json', 'xml', 'yaml', 'yml'
}

SAFE_INLINE_MIMES = {
    'image/jpeg', 'image/png', 'image/webp', 
    'audio/mpeg', 'audio/ogg', 'audio/wav', 
    'video/mp4', 'application/pdf'
}

def is_extension_allowed(filename):
    if not filename:
        return False
    
    ext = Path(filename).suffix.lstrip('.').lower()
    
    return ext in ALLOWED_EXTENSIONS

MAX_FILE_SIZE = 50 * 1024 * 1024

def sign_binary_data(binary_data, private_key_pem):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )
    signature = private_key.sign(
        binary_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

class WorkListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [CryptoOpsRateThrottle]
    
    def get(self, request):
        user = request.user
        
        if user.groups.filter(name="Author").exists():
            queryset = Work.objects.filter(author=user)
            
        else:
            queryset = Work.objects.filter(status='published')
            
        serializer = WorkSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data
        work_type = data.get('work_type')
        
        if not request.user.has_perm('works.add_work'):
            return Response(
                {"error": "Tu cuenta no tiene permisos para registrar nuevas obras en la plataforma."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = WorkSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        clean_data = serializer.validated_data
        
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
            for k, v in clean_data.items():
                if k != 'file_upload' and k != 'resume_upload' and v != "":
                    if k in valid_fields:
                        create_data[k] = v
                    
            plan_id = data.get('plan_required')
            
            if plan_id:
                create_data['plan_required'] = SubscriptionPlan.objects.get(id=plan_id)
                
            else:
                create_data['plan_required'] = None
            
            if work_type in ['paint', 'sculpture'] and 'type_detail' in clean_data:
                create_data['type'] = clean_data['type_detail']
            
            file = request.FILES.get('file_upload')
            resume = request.FILES.get('resume_upload')
            
            if not file:
                return Response({"error": "Es obligatorio adjuntar un archivo para registrar y firmar la obra."}, status=status.HTTP_400_BAD_REQUEST)

            if file.size > MAX_FILE_SIZE or (resume and resume.size > MAX_FILE_SIZE):
                return Response({"error": "El archivo excede el tamaño máximo permitido (50 MB)."}, status=status.HTTP_400_BAD_REQUEST)

            if not is_extension_allowed(file.name) or (resume and not is_extension_allowed(resume.name)):
                return Response({"error": "Formato de archivo no permitido."}, status=status.HTTP_400_BAD_REQUEST)

            file_info = process_file_for_ai(file)
            file.seek(0)
            
            resume_info = None
            if resume:
                resume_info = process_file_for_ai(resume)
                resume.seek(0)

            result_ai_validator = validate_work_content(clean_data.get('title'), clean_data.get('description'), file_info, resume_info)
            ai_is_valid = result_ai_validator.get("is_valid")
            
            request_review_raw = request.data.get('request_manual_review', False)

            raw_str = str(request_review_raw).strip().lower()
            if raw_str in ['true', '1', 'yes', 't']:
                wants_manual_review = True
                
            else:
                wants_manual_review = False

            if ai_is_valid:
                create_data['status'] = 'published'
                
            else:
                if wants_manual_review:
                    create_data['status'] = 'appealed'
                    create_data['rejection_reason'] = result_ai_validator.get('reason', 'Contenido no apto según IA')
                    
                else:
                    return Response(
                        {"error": f"La obra fue rechazada por el sistema de validación: {result_ai_validator.get('reason')}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            user_private_key_pem = request.user.private_key
        
            if not user_private_key_pem:
                return Response({"error": "El usuario no dispone de una clave privada para firmar."}, status=status.HTTP_400_BAD_REQUEST)
            
            binary_file = file.read()
            clean_filename = Path(file.name).name
            create_data['binary_file'] = binary_file
            create_data['file_name'] = clean_filename
            create_data['file_type'] = file.content_type
            create_data['hash_security'] = sign_binary_data(binary_file, user_private_key_pem)
                
            if resume:
                clean_resume_name = Path(resume.name).name
                create_data['resume_file'] = resume.read()
                create_data['resume_name'] = clean_resume_name
                create_data['resume_type'] = resume.content_type
                                
            obj = model_class.objects.create(author=request.user, **create_data)
            
            subscriptions = AuthorSubscription.objects.filter(author=request.user)
            
            if obj.status == 'published':
                subscriptions = AuthorSubscription.objects.filter(author=request.user)
                notifications_to_create = []
                for sub in subscriptions:
                    notifications_to_create.append(
                        Notification(
                            recipient=sub.consumer,
                            notification_type='new_work',
                            work=obj,
                            message=f"El autor {request.user.username} ha publicado una nueva obra: '{obj.title}'"
                        )
                    )
                    
                if notifications_to_create:
                    Notification.objects.bulk_create(notifications_to_create)
                
            return Response(WorkSerializer(obj).data, status=status.HTTP_201_CREATED)
                        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class WorkDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        serializer = WorkSerializer(work)
        return Response(serializer.data)
     
    def patch(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        user = request.user

        if work.author != user:
            return Response(
                {"error": "No tienes permiso para modificar esta obra."},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if new_status:
            if new_status == 'published':
                if work.status not in ['approved', 'published']:
                    return Response(
                        {"error": "Solo puedes publicar obras previamente aprobadas por el equipo de moderación."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                work.status = 'published'
                work.save()

                subscriptions = AuthorSubscription.objects.filter(author=work.author)
                notifications_to_create = []
                for sub in subscriptions:
                    notifications_to_create.append(
                        Notification(
                            recipient=sub.consumer,
                            notification_type='new_work',
                            work=work,
                            message=f"El autor {work.author.username} ha publicado una nueva obra: '{work.title}'"
                        )
                    )
                if notifications_to_create:
                    Notification.objects.bulk_create(notifications_to_create)

            else:
                work.status = new_status
                work.save()

        serializer = WorkSerializer(work)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        
        if(work.author != request.user):
            return Response(
            {"error": "No tienes permiso para eliminar esta obra."}, 
            status=status.HTTP_403_FORBIDDEN
        )
        
        work.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ListWorksByAuthorAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id):
        user = request.user

        is_owner = (user.id == int(author_id))
        
        if is_owner:
            queryset = Work.objects.filter(author_id=author_id)
            
        else:
            queryset = Work.objects.filter(status__in=['published'], author_id=author_id)
        
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
            
        safe_name = Path(work.file_name).name
        disposition = 'inline' if work.file_type in SAFE_INLINE_MIMES else 'attachment'
        
        response = HttpResponse(work.binary_file, content_type=work.file_type or 'application/octet-stream')
        response['Content-Disposition'] = f'{disposition}; filename="{safe_name}"'
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    
class ServeWorkResumeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        work = get_object_or_404(Work, pk=pk)
        
        if not work.resume_file:
            return HttpResponse("Esta obra no dispone de muestra gratuita.", status=404)
        
        safe_name = Path(work.resume_name).name
        disposition = 'inline' if work.resume_type in SAFE_INLINE_MIMES else 'attachment'
        
        response = HttpResponse(work.resume_file, content_type=work.resume_type or 'application/octet-stream')
        response['Content-Disposition'] = f'{disposition}; filename="preview_{safe_name}"'
        return response
    
class RecommendedWorksAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        consumer = request.user
        
        recommended_authors = get_recommended_authors_for_user(consumer)
        
        if not recommended_authors:
            interests = consumer.interests or ""
            interests_list = [i.strip() for i in interests.split(',') if i.strip()]
            
            recommended_works = Work.objects.filter(status='published', work_type__in=interests_list)
            
        else:
            recommended_works = Work.objects.filter(status='published', author__in=recommended_authors)
                    
        recommended_works = recommended_works.distinct().order_by('-created_at')[:20]
        
        serializer = WorkSerializer(recommended_works, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)