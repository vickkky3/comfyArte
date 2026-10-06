from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from subscriptions.models import SubscriptionPlan, AuthorSubscription
from users.models import Notification
from ..models import Work, Book, Music, Video, Software, Paint, Sculpture
from ..serializers import WorkSerializer
from works.services import get_recommended_authors_for_user

User = get_user_model()


class WorkModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="author1", password="password123")

    def test_child_models_polymorphic_type(self):
        book = Book.objects.create(
            title="El Quijote",
            description="Novela clásica",
            author=self.user,
            work_type="book",
            pages=800,
            isbn="978-84-376-0494-7",
            genre="Novela",
            language="Español"
        )
        
        self.assertEqual(book.get_work_type(), "book")
        self.assertEqual(book.title, "El Quijote")
        self.assertEqual(book.description, "Novela clásica")
        self.assertEqual(book.author.username, "author1")
        self.assertEqual(book.pages, 800)
        self.assertEqual(book.isbn, "978-84-376-0494-7")
        self.assertEqual(book.genre, "Novela")
        self.assertEqual(book.language, "Español")

        music = Music.objects.create(
            title="Susurros",
            description="Música urbana",
            author=self.user,
            work_type="music",
            duration=3.15,
            album="Doble",
            genre="rock"
        )
        
        self.assertEqual(music.get_work_type(), "music")
        self.assertEqual(music.title, "Susurros")
        self.assertEqual(music.description, "Música urbana")
        self.assertEqual(music.author.username, "author1")
        self.assertEqual(music.duration, 3.15)
        self.assertEqual(music.album, "Doble")
        self.assertEqual(music.genre, "rock")
        
        video = Video.objects.create(
            title="Cortometraje",
            description="Un cortometraje de suspense",
            author=self.user,
            work_type="video",
            duration=10.15,
            genre="short_film"
        )
        
        self.assertEqual(video.get_work_type(), "video")
        self.assertEqual(video.title, "Cortometraje")
        self.assertEqual(video.description, "Un cortometraje de suspense")
        self.assertEqual(video.author.username, "author1")
        self.assertEqual(video.duration, 10.15)
        self.assertEqual(video.genre, "short_film")
        
        software = Software.objects.create(
            title="Microservicio de Autenticación Criptográfica",
            description="Módulo en Python para la generación y validación de firmas digitales.",
            author=self.user,
            work_type="software",
            repository_url="https://github.com/cascon-dev/crypto-auth-service",
            documentation_url="https://docs.cascon-dev.org/crypto-auth/",
        )
        
        self.assertEqual(software.get_work_type(), "software")
        self.assertEqual(software.title, "Microservicio de Autenticación Criptográfica")
        self.assertEqual(software.description, "Módulo en Python para la generación y validación de firmas digitales.")
        self.assertEqual(software.author.username, "author1")
        self.assertEqual(software.repository_url, "https://github.com/cascon-dev/crypto-auth-service")
        self.assertEqual(software.documentation_url, "https://docs.cascon-dev.org/crypto-auth/")

        paint = Paint.objects.create(
            title="Lienzo al óleo",
            description="Pintura clásica",
            author=self.user,
            work_type="paint",
            height=100.0,
            weight=3.5,
            type="oil"
        )
        
        self.assertEqual(paint.get_work_type(), "paint")
        self.assertEqual(paint.get_type_display(), "Óleo")
        self.assertEqual(paint.type, "oil")
        self.assertEqual(paint.title, "Lienzo al óleo")
        self.assertEqual(paint.description, "Pintura clásica")
        self.assertEqual(paint.author.username, "author1")
        self.assertEqual(paint.height, 100.0)
        self.assertEqual(paint.weight, 3.5)
        
        sculpture = Sculpture.objects.create(
            title="Suspendido",
            description="Pieza volumétrica abstracta trabajada en fundición metálica y soporte pétreo.",
            author=self.user,
            work_type="sculpture",
            height=145,
            weight=18.5,
            type="bronze"
        )
        
        self.assertEqual(sculpture.get_work_type(), "sculpture")
        self.assertEqual(sculpture.get_type_display(), "Bronce")
        self.assertEqual(sculpture.type, "bronze")
        self.assertEqual(sculpture.title, "Suspendido")
        self.assertEqual(sculpture.description, "Pieza volumétrica abstracta trabajada en fundición metálica y soporte pétreo.")
        self.assertEqual(sculpture.author.username, "author1")
        self.assertEqual(sculpture.height, 145)
        self.assertEqual(sculpture.weight, 18.5)


class WorkSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="author_ser", password="password123")

    def test_bleach(self):
        malicious_data = {
            "title": "Obra <script>alert('xss')</script>",
            "description": "Texto <b onclick='hack()'>con</b> HTML",
            "license": "by",
            "work_type": "book",
            "isbn": "<script>evil()</script>123456",
            "pages": 150,
            "genre": "comic",
            "language": "es",
        }
        serializer = WorkSerializer(data=malicious_data)
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["title"], "Obra alert('xss')")
        self.assertEqual(serializer.validated_data["description"], "Texto con HTML")
        self.assertEqual(serializer.validated_data["isbn"], "evil()123456")

    def test_representation_includes_submodel_fields_and_omits_binary_content(self):
        music = Music.objects.create(
            title="Susurros",
            description="Música urbana",
            author=self.user,
            work_type="music",
            duration=3.15,
            album="Doble",
            genre="rock",
            binary_file=b"\x00\x01\x02\x03",
            file_name="cancion.mp3",
            file_type="audio/mpeg"
        )
        serializer = WorkSerializer(instance=music)
        data = serializer.data

        self.assertEqual(data["duration"], 3.15)
        self.assertEqual(data["album"], "Doble")
        self.assertEqual(data["music_genre"], "Rock")
        self.assertEqual(data["file_name"], "cancion.mp3")

        self.assertNotIn("binary_file", data)
        self.assertNotIn("resume_file", data)


class WorkAPITests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username="autor_api", password="password123")
        self.consumer = User.objects.create_user(username="consumer_api", password="password123")

        author_group, _ = Group.objects.get_or_create(name="Author")
        consumer_group, _ = Group.objects.get_or_create(name="Consumer")

        view_work_perm = Permission.objects.get(codename="view_work", content_type__app_label="works")
        add_work_perm = Permission.objects.get(codename="add_work", content_type__app_label="works")
        delete_work_perm = Permission.objects.get(codename="delete_work", content_type__app_label="works")

        author_group.permissions.add(view_work_perm, add_work_perm, delete_work_perm)
        consumer_group.permissions.add(view_work_perm)

        self.author.groups.add(author_group)
        self.consumer.groups.add(consumer_group)

        self.plan = SubscriptionPlan.objects.create(name="Plan básico", price=4.99)

    @patch("works.views.validate_work_content")
    @patch("works.views.process_file_for_ai")
    def test_post_work_published_on_ai_approval(self, mock_process_ai, mock_validate_ai):
        self.client.force_authenticate(user=self.author)

        mock_process_ai.return_value = {"type": "media", "size": 100}
        mock_validate_ai.return_value = {"is_valid": True}

        dummy_main_file = SimpleUploadedFile("audio.wav", b"Obra prueba", content_type="audio/wav")
        dummy_resume_file = SimpleUploadedFile("preview.ogg", b"Resumen prueba", content_type="audio/ogg")

        payload = {
            "title": "Susurros",
            "description": "Música urbana",
            "work_type": "music",
            "license": "by",
            "duration": 3.15,
            "album": "Doble",
            "music_genre": "rock",
            "file_upload": dummy_main_file,
            "resume_upload": dummy_resume_file,
            "plan_required": self.plan.id
        }

        response = self.client.post("/api/works/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "published")
        self.assertEqual(response.data["title"], "Susurros")

        created_work = Music.objects.get(title="Susurros")
        self.assertEqual(created_work.author, self.author)
        self.assertEqual(created_work.duration, 3.15)
        self.assertTrue(len(created_work.hash_security) > 0)
        self.assertEqual(created_work.binary_file, b"Obra prueba")

    @patch("works.views.validate_work_content")
    @patch("works.views.process_file_for_ai")
    def test_post_work_rejected_with_manual_review_appealed(self, mock_process_ai, mock_validate_ai):
        self.client.force_authenticate(user=self.author)

        mock_process_ai.return_value = {"type": "code"}
        mock_validate_ai.return_value = {"is_valid": False, "reason": "Uso de palabras restringidas"}

        py_file = SimpleUploadedFile("script.py", b"print('hola')", content_type="text/x-python")

        payload = {
            "title": "Software Inseguro",
            "description": "Script de test",
            "work_type": "software",
            "license": "by",
            "programming_language": "Python",
            "file_upload": py_file,
            "request_manual_review": "true"
        }

        response = self.client.post("/api/works/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "appealed")
        self.assertEqual(response.data["rejection_reason"], "Uso de palabras restringidas")

    def test_post_work_forbidden_without_permission(self):
        user_sin_permiso = User.objects.create_user(username="no_perm", password="password123")
        self.client.force_authenticate(user=user_sin_permiso)

        file = SimpleUploadedFile("test.pdf", b"%PDF-dummy", content_type="application/pdf")
        response = self.client.post("/api/works/", {"title": "X", "file_upload": file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_work_fails_with_disallowed_extension(self):
        self.client.force_authenticate(user=self.author)

        exe_file = SimpleUploadedFile("virus.exe", b"binary", content_type="application/x-msdownload")
        payload = {
            "title": "Programa Malicioso",
            "description": "Test",
            "work_type": "software",
            "license": "by",
            "programming_language": "Python",
            "file_upload": exe_file
        }

        response = self.client.post("/api/works/", payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Formato de archivo no permitido", response.data["error"])

    def test_serve_work_binary_file_and_resume_headers(self):
        self.client.force_authenticate(user=self.consumer)

        work = Work.objects.create(
            title="Documento",
            description="Descripción",
            author=self.author,
            binary_file=b"Obra prueba",
            file_name="manual.pdf",
            file_type="application/pdf",
            resume_file=b"Muestra prueba",
            resume_name="muestra.txt",
            resume_type="text/plain",
            status="published"
        )

        res_file = self.client.get(f"/api/works/{work.id}/serve/")
        self.assertEqual(res_file.status_code, status.HTTP_200_OK)
        self.assertEqual(res_file.content, b"Obra prueba")

        res_resume = self.client.get(f"/api/works/{work.id}/serve-resume/")
        self.assertEqual(res_resume.status_code, status.HTTP_200_OK)
        self.assertEqual(res_resume.content, b"Muestra prueba")

    def test_patch_and_delete_work_permissions(self):
        work = Work.objects.create(
            title="Mi Obra",
            description="Descripción",
            author=self.author,
            status="approved"
        )

        self.client.force_authenticate(user=self.consumer)
        patch_res = self.client.patch(f"/api/works/{work.id}/", {"status": "published"}, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.author)
        patch_ok = self.client.patch(f"/api/works/{work.id}/", {"status": "published"}, format="json")
        self.assertEqual(patch_ok.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_ok.data["status"], "published")

        delete_res = self.client.delete(f"/api/works/{work.id}/")
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Work.objects.filter(id=work.id).exists())
        
User = get_user_model()


class RecommendationServiceTests(TestCase):

    def setUp(self):
        self.user_a = User.objects.create_user(username="user_a", password="password123")
        self.user_b = User.objects.create_user(username="user_b", password="password123")
        self.user_without_subscriptions = User.objects.create_user(username="user_new", password="password123")

        self.author_1 = User.objects.create_user(username="author_1", password="password123")
        self.author_2 = User.objects.create_user(username="author_2", password="password123")
        self.author_3 = User.objects.create_user(username="author_3", password="password123")

    def test_collaborative_filtering_recommends_unfollowed_author(self):

        AuthorSubscription.objects.create(consumer=self.user_a, author=self.author_1)

        AuthorSubscription.objects.create(consumer=self.user_b, author=self.author_1)
        AuthorSubscription.objects.create(consumer=self.user_b, author=self.author_2)

        recommendations = get_recommended_authors_for_user(self.user_a)

        self.assertIn(self.author_2, recommendations)
        self.assertNotIn(self.author_1, recommendations) 
        self.assertEqual(len(recommendations), 1)

    def test_exclude_already_subscribed_authors(self):
        AuthorSubscription.objects.create(consumer=self.user_a, author=self.author_1)
        AuthorSubscription.objects.create(consumer=self.user_a, author=self.author_2)

        AuthorSubscription.objects.create(consumer=self.user_b, author=self.author_1)
        AuthorSubscription.objects.create(consumer=self.user_b, author=self.author_2)

        recommendations = get_recommended_authors_for_user(self.user_a)
        self.assertEqual(recommendations, [])

    def test_exception_handling_returns_empty_list(self):
        
        with patch("subscriptions.models.AuthorSubscription.objects.filter", side_effect=Exception("DB Error")):
            recommendations = get_recommended_authors_for_user(self.user_a)
            self.assertEqual(recommendations, [])


class RecommendedWorksAPITests(APITestCase):
    def setUp(self):
        self.consumer = User.objects.create_user(
            username="lector", 
            password="password123",
            interests="music,video"
        )
        
        perm_view = Permission.objects.get(codename="view_work", content_type__app_label="works")
        self.consumer.user_permissions.add(perm_view)

        self.author_rec = User.objects.create_user(username="musico", password="password123")
        self.client.force_authenticate(user=self.consumer)

    @patch("works.views.get_recommended_authors_for_user")
    def test_recommended_works_by_collaborative_authors(self, mock_get_rec_authors):

        mock_get_rec_authors.return_value = [self.author_rec]

        music = Work.objects.create(
            title="Ecos del Atardecer",
            description="Musica",
            author=self.author_rec,
            work_type="music",
            status="published"
        )

        Work.objects.create(
            title="Borrador",
            description="No visible",
            author=self.author_rec,
            work_type="music",
            status="pending_ai"
        )

        response = self.client.get("/api/works/recommended/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], music.id)
        self.assertEqual(response.data[0]["title"], "Ecos del Atardecer")

    @patch("works.views.get_recommended_authors_for_user")
    def test_fallback_to_user_interests_when_no_author_recommendations(self, mock_get_rec_authors):
        mock_get_rec_authors.return_value = []

        other_author = User.objects.create_user(username="other_author", password="password123")

        Work.objects.create(
            title="Ecos del Atardecer",
            description="Musica",
            author=other_author,
            work_type="music",
            status="published"
        )
        Work.objects.create(
            title="El enigma de las sombras",
            description="Libro",
            author=other_author,
            work_type="book",
            status="published"
        )

        response = self.client.get("/api/works/recommended/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        title = [w["title"] for w in response.data]
        self.assertIn("Ecos del Atardecer", title)
        self.assertNotIn("El enigma de las sombras", title)