import openai
import json
import io
import base64

from pypdf import PdfReader
from django.conf import settings
from subscriptions.models import AuthorSubscription

max_chars = 5000

def validate_work_content(title, description, file_info, resume_info):
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = f"""
    Eres un auditor de contenidos para la plataforma de propiedad intelectual ComfyARTE.
    Tu única función es actuar como filtro de seguridad contra contenido estrictamente indebido o ilegal.

    DATOS DE LA OBRA:
    - Título: {title}
    - Descripción: {description}
    """

    if file_info[0] == 'text' and file_info[1]:
        prompt += f"\n- Texto extraído de la obra: {file_info[1]}"
    if resume_info[0] == 'text' and resume_info[1]:
        prompt += f"\n- Texto extraído de la muestra: {resume_info[1]}"

    prompt += """


    REGLAS DE EVALUACIÓN (CRITERIO DE RECHAZO ESTRICTO):

    1. QUÉ DEBES RECHAZAR OBLIGATORIAMENTE (is_valid: false):
       - Contenido explícito no permitido, pornografía o violencia gráfica.
       - Discurso de odio, acoso, discriminación o incitación a la violencia.
       - Promoción de actividades ilegales, estafas, malware o vulneraciones de seguridad.
       - Spam evidente (secuencias aleatorias de caracteres sin sentido alguno).

    2. QUÉ DEBES ACEPTAR SIEMPRE (is_valid: true):
       - Obras sencillas, cortas, principiantes, infantiles o de tema cotidiano.
       - Textos breves, código fuente simple, composiciones básicas o imágenes minimalistas.
       - NO evalúes la calidad artística, la complejidad técnica ni el valor comercial.
       - Si la obra no incumple ninguna regla de contenido indebido, debes aprobarla.

    Responde estrictamente en formato JSON:
    {{"is_valid": true/false, "reason": "Si se aprueba, indica 'Obra apta para publicación'. Si se rechaza, explica el motivo exacto en español."}}
    """
    
    user_payload = [{"type": "text", "text": prompt}]
    
    if file_info[0] == 'image':
        user_payload.append({
            "type": "image_url",
            "image_url": {"url": f"data:{file_info[1]['mime']};base64,{file_info[1]['b64']}"}
        })


    if resume_info[0] == 'image':
        user_payload.append({
            "type": "image_url",
            "image_url": {"url": f"data:{resume_info[1]['mime']};base64,{resume_info[1]['b64']}"}
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_payload}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "is_valid": False,
            "reason": f"Error al procesar la validación con la IA: {str(e)}"
        }
    
def process_file_for_ai(file_obj):
    
    
    if not file_obj:
        return 'none', None
    
    filename = file_obj.name.lower()
    content_type = getattr(file_obj, 'content_type', '').lower()
    
    file_bytes = file_obj.read()
    file_obj.seek(0)

    if filename.endswith('.pdf') or 'pdf' in content_type:
        return process_pdf_for_ai(file_bytes)
        

    elif any(filename.endswith('.' + ext) for ext in ['jpg', 'jpeg', 'png', 'webp']) or content_type.startswith('image/'):
        b64_image = base64.b64encode(file_bytes).decode('utf-8')
        mime = content_type if content_type.startswith('image/') else 'image/jpeg'
        return 'image', {'b64': b64_image, 'mime': mime}
    
    elif any(filename.endswith('.' + ext) for ext in ['mp3', 'wav', 'ogg']) or content_type.startswith('audio/'):
        return process_audio_for_ai(file_bytes, filename)
    
    elif any(filename.endswith('.' + ext) for ext in ['py', 'js', 'ts', 'jsx', 'tsx', 'vue', 'html', 'css', 'java', 'c', 'cpp', 'cs', 'php', 'rb', 'go', 'rs', 'swift', 'kt', 'sql', 'sh', 'ipynb', 'json', 'xml', 'yaml', 'yml']):
        try:
            code_text = file_bytes.decode('utf-8', errors='ignore')
            return 'text', code_text[:max_chars]
        
        except Exception:
            return 'none', None

    return 'none', None

def process_pdf_for_ai(file_bytes):
    try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
                if len(text) >= max_chars:
                    break
                
            return 'text', text[:max_chars]
        
    except Exception:
        return 'none', None

def process_audio_for_ai(file_bytes, filename):
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        audio_file = io.BytesIO(file_bytes)
        audio_file.name = filename
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return 'text', transcript.text[:max_chars]
    
    except Exception:
        return 'none', None      

def get_recommended_authors_for_user(user):
    try:
        my_author_ids = AuthorSubscription.objects.filter(
            consumer=user
        ).values_list('author_id', flat=True)

        if not my_author_ids:
            return []

        similar_consumer_ids = AuthorSubscription.objects.filter(
            author_id__in=my_author_ids
        ).exclude(consumer=user).values_list('consumer_id', flat=True)

        recommended_subscriptions = AuthorSubscription.objects.filter(
            consumer_id__in=similar_consumer_ids
        ).exclude(
            author_id__in=my_author_ids
        ).select_related('author')

        recommended_authors = list({sub.author for sub in recommended_subscriptions})
        return recommended_authors

    except Exception as e:
        print(f"Error en recomendación: {e}")
        return []
        