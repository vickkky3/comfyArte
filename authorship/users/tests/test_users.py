from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import Notification
from users.serializers import UserSerializer, AuthorPublicSerializer, NotificationSerializer
from works.models import Work

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.user_author = User.objects.create_user(
            first_name="Elena",
            last_name="Vázquez",
            username="elena_art",
            email="elena.vazquez@example.com",
            password="TFGTest2026!",
            role="author",
            biography="Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual."
        )
        
        self.user_consumer = User.objects.create_user(
            first_name="Carlos",
            last_name="Navarro",
            username="carlos_reader",
            email="carlos.navarro@example.com",
            password="TFGTest2026!",
            role="consumer",
            interests="book,music,paint"
        )
        
    def test_create_user_author(self):
        self.assertEqual(self.user_author.first_name, "Elena")
        self.assertEqual(self.user_author.last_name, "Vázquez")
        self.assertEqual(self.user_author.username, "elena_art")
        self.assertEqual(self.user_author.email, "elena.vazquez@example.com")
        self.assertEqual(self.user_author.role, "author")
        self.assertEqual(self.user_author.biography, "Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.")
        self.assertTrue(self.user_author.check_password("TFGTest2026!"))

    def test_create_user_consumer(self):
        self.assertEqual(self.user_consumer.first_name, "Carlos")
        self.assertEqual(self.user_consumer.last_name, "Navarro")
        self.assertEqual(self.user_consumer.username, "carlos_reader")
        self.assertEqual(self.user_consumer.email, "carlos.navarro@example.com")
        self.assertEqual(self.user_consumer.role, "consumer")
        self.assertEqual(self.user_consumer.interests, "book,music,paint")
        self.assertTrue(self.user_consumer.check_password("TFGTest2026!"))

    def test_notification_creation_and_str(self):
        notification = Notification.objects.create(
            recipient=self.user_consumer,
            notification_type="new_work",
            message="Se ha publicado una nueva obra"
        )
        
        self.assertEqual(notification.recipient, self.user_consumer)
        self.assertEqual(
            str(notification),
            f"Notificación (new_work) para {self.user_consumer.username}"
        )


class UserSerializerTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "username": "carlos_reader",
            "email": "carlos.navarro@example.com",
            "password": "TFGTest2026!",
            "first_name": "Carlos",
            "last_name": "Navarro",
            "role": "consumer",
            "interests": "book,music,paint"
        }

    def test_serializer_creates_user_with_hashed_password(self):
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        user = serializer.save()

        self.assertEqual(user.username, "carlos_reader")
        self.assertTrue(user.check_password("TFGTest2026!"))
        self.assertNotEqual(user.password, "TFGTest2026!")

    def test_serializer_cleans_xss_tags_with_bleach(self):
        data_xss = self.valid_data.copy()
        data_xss["first_name"] = "<b>Juan</b>"
        data_xss["last_name"] = "<script>alert('xss')</script>Perez"
        data_xss["biography"] = "<p>Hola <a href='malicious.com'>mundo</a></p>"

        serializer = UserSerializer(data=data_xss)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["first_name"], "Juan")
        self.assertEqual(serializer.validated_data["last_name"], "alert('xss')Perez")
        self.assertEqual(serializer.validated_data["biography"], "Hola mundo")

    def test_username_with_spaces_fails_validation(self):
        data_space = self.valid_data.copy()
        data_space["username"] = "usuario con espacios"

        serializer = UserSerializer(data=data_space)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertIn("no puede contener espacios", str(serializer.errors["username"]))

    def test_invalid_email_format_fails_validation(self):
        data_bad_mail = self.valid_data.copy()
        data_bad_mail["email"] = "no-es-un-email"

        serializer = UserSerializer(data=data_bad_mail)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_is_write_only(self):
        user = User.objects.create_user(**self.valid_data)
        serializer = UserSerializer(instance=user)
        
        self.assertNotIn("password", serializer.data)

    def test_author_public_serializer_exposes_only_safe_fields(self):
        user = User.objects.create_user(**self.valid_data)
        serializer = AuthorPublicSerializer(instance=user)
        
        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "username", "first_name", "last_name", "biography", "role"}
        )
        self.assertNotIn("email", serializer.data)


class UserAPITests(APITestCase):
    def setUp(self):
        self.group_author = Group.objects.create(name="Author")
        self.group_consumer = Group.objects.create(name="Consumer")

        self.author_user = User.objects.create_user(
            first_name="Lucía",
            last_name="Navarro",
            username="lucia_beats",
            email="lucia.beats@example.com",
            password="TFGTest2026!",
            role="author",
            biography="Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual."
        )
        
        self.author_user.groups.add(self.group_author)
        self.author_token = Token.objects.create(user=self.author_user)

        self.consumer_user = User.objects.create_user(
            first_name="Lucas",
            last_name="López",
            username="lucas_consumer",
            email="lucas.lopez@example.com",
            password="TFGTest2026!",
            role="consumer",
            interests="book,paint"
        )
        self.consumer_user.groups.add(self.group_consumer)
        self.consumer_token = Token.objects.create(user=self.consumer_user)

    def test_register_author_creates_user_group_and_token(self):
        self.client.credentials()
        payload = {
            "username": "elena_art",
            "email": "elena.vazquez@example.com",
            "password": "TFGTest2026!",
            "first_name": "Elena",
            "last_name": "Navarro",
            "role": "author"
        }

        response = self.client.post("/api/users/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="elena_art")
        self.assertEqual(user.role, "author")
        self.assertTrue(user.groups.filter(name="Author").exists())
        self.assertFalse(user.groups.filter(name="Consumer").exists())
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_register_consumer_creates_consumer_group(self):
        self.client.credentials()
        payload = {
            "username": "carlos_reader",
            "email": "carlos.navarro@example.com",
            "password": "TFGTest2026!",
            "first_name": "Carlos",
            "last_name": "Navarro",
            "role": "consumer"
        }

        response = self.client.post("/api/users/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="carlos_reader")
        self.assertEqual(user.role, "consumer")
        self.assertTrue(user.groups.filter(name="Consumer").exists())

    def test_get_current_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.author_token.key)
        response = self.client.get("/api/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "lucia_beats")
        self.assertTrue(response.data["es_autor"])
        self.assertFalse(response.data["es_consumidor"])

    def test_patch_current_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.author_token.key)
        payload = {
            "biography": "Nueva biografía actualizada",
        }
        response = self.client.patch("/api/users/me/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author_user.refresh_from_db()
        self.assertEqual(self.author_user.biography, "Nueva biografía actualizada")
        
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.consumer_token.key)
        payload = { 
            "interests": "software,painting"
        }
        response = self.client.patch("/api/users/me/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consumer_user.refresh_from_db()
        self.assertEqual(self.consumer_user.interests, "software,painting")

    def test_author_list_only_returns_authors(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.consumer_token.key)
        response = self.client.get("/api/users/authors/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u["username"] for u in response.data]
        self.assertIn("lucia_beats", usernames)
        self.assertNotIn("consumidor_test", usernames)

    def test_notifications_list_only_returns_recipient_notifications(self):
        Notification.objects.create(
            recipient=self.author_user,
            sender=self.consumer_user,
            notification_type="new_follower",
            message="Lucas te ha seguido"
        )
        
        Notification.objects.create(
            recipient=self.consumer_user,
            sender=self.author_user,
            notification_type="new_work",
            message="Lucía subió una obra"
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.author_token.key)
        response = self.client.get("/api/users/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "Lucas te ha seguido")
        self.assertEqual(response.data[0]["notification_type"], "new_follower")
        
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.consumer_token.key)
        response = self.client.get("/api/users/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "Lucía subió una obra")
        self.assertEqual(response.data[0]["notification_type"], "new_work")

    def test_unauthenticated_request_fails(self):
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)