from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from subscriptions.models import (
    SubscriptionPlan,
    UserSubscription,
    UserWallet,
    AuthorSubscription,
    SaveWork,
)
from subscriptions.serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    UserWalletSerializer,
    SaveWorkSerializer,
)
from users.models import Notification
from works.models import Work

User = get_user_model()


class SubscriptionModelsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", password="password123")

    def test_subscription_plan_points_calculation_on_save(self):
        plan_creator = SubscriptionPlan.objects.create(
            name="Plan Creador",
            price=Decimal("4.99"),
            description="Acceso al catálogo digital estándar, audios completos y resolución HD"
        )
        self.assertEqual(plan_creator.points, 50)
        self.assertEqual(str(plan_creator), "Plan Creador (50 pts)")

        plan_pro = SubscriptionPlan.objects.create(
            name="Plan Mecenas",
            price=Decimal("9.94"),
            description="Acceso a obras exclusivas, descargas de código/ficheros originales y contacto directo"
        )
        self.assertEqual(plan_pro.points, 99)

    def test_user_subscription_is_valid_method(self):
        plan = SubscriptionPlan.objects.create(name="Básico", price=Decimal("2.99"))
        
        sub_activa = UserSubscription.objects.create(
            user=self.user,
            plan=plan,
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )
        self.assertTrue(sub_activa.is_valid())

        sub_activa.end_date = timezone.now() - timedelta(days=1)
        sub_activa.save()
        self.assertFalse(sub_activa.is_valid())

        sub_activa.end_date = timezone.now() + timedelta(days=30)
        sub_activa.active = False
        sub_activa.save()
        self.assertFalse(sub_activa.is_valid())


class SubscriptionSerializersTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(username="elena_art", role="author")
        self.consumer = User.objects.create_user(username="carlos_reader", role="consumer")
        self.plan = SubscriptionPlan.objects.create(name="Plan Mecenas", price=Decimal("15.00"))

    def test_user_subscription_serializer_read_only_fields(self):
        sub = UserSubscription.objects.create(
            user=self.consumer,
            plan=self.plan,
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )
        serializer = UserSubscriptionSerializer(instance=sub)
        
        self.assertEqual(serializer.data["plan_name"], "Plan Mecenas")
        self.assertEqual(serializer.data["plan_points"], 150)

    def test_save_work_serializer(self):
        work = Work.objects.create(
            title="Ecos del Atardecer",
            description="Composición ambiental instrumental producida con sintetizadores analógicos y ritmos suaves.",
            author=self.author,
            work_type="music",
            status="published"
        )
        saved = SaveWork.objects.create(consumer=self.consumer, work=work)
        serializer = SaveWorkSerializer(instance=saved)

        self.assertEqual(serializer.data["title"], "Ecos del Atardecer")
        self.assertEqual(serializer.data["work_type"], "music")
        self.assertEqual(serializer.data["author_username"], "elena_art")
        self.assertEqual(serializer.data["work_id"], work.id)


class SubscriptionAPITests(APITestCase):

    def setUp(self):
        self.author = User.objects.create_user(username="lucia_beats", password="TFGTest2026!", role="author")
        self.consumer = User.objects.create_user(username="lucas_lopez", password="TFGTest2026!", role="consumer")

        self.plan = SubscriptionPlan.objects.create(
            name="Plan Creador",
            price=Decimal("5.00"),
            duration_days=30
        )

        self.wallet = UserWallet.objects.create(user=self.consumer, points=150)
        self.client.force_authenticate(user=self.consumer)

    def test_get_subscription_plans(self):
        response = self.client.get("/api/subscriptions/plans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Plan Creador")

    def test_subscribe_success(self):
        payload = {"plan_id": self.plan.id}
        response = self.client.post("/api/subscriptions/subscribe/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.points, 100)

        sub = UserSubscription.objects.get(user=self.consumer)
        self.assertTrue(sub.active)
        self.assertEqual(sub.plan, self.plan)

    def test_subscribe_fails_if_already_active(self):
        UserSubscription.objects.create(
            user=self.consumer,
            plan=self.plan,
            end_date=timezone.now() + timedelta(days=30),
            active=True
        )

        response = self.client.post("/api/subscriptions/subscribe/", {"plan_id": self.plan.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ya tienes una suscripción activa", response.data["detail"])

    def test_subscribe_fails_insufficient_funds(self):
        self.wallet.points = 10
        self.wallet.save()

        response = self.client.post("/api/subscriptions/subscribe/", {"plan_id": self.plan.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("No tienes puntos suficientes", response.data["detail"])

    def test_my_subscription_notifies_when_one_day_left(self):
        UserSubscription.objects.create(
            user=self.consumer,
            plan=self.plan,
            end_date=timezone.now() + timedelta(days=1),
            active=True
        )

        response = self.client.get("/api/subscriptions/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notif = Notification.objects.filter(recipient=self.consumer, notification_type="plan_expiring")
        self.assertTrue(notif.exists())

    def test_author_subscription_and_notification(self):
        payload = {"author_id": self.author.id}
        response = self.client.post("/api/subscriptions/authors/subscribe/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(AuthorSubscription.objects.filter(consumer=self.consumer, author=self.author).exists())

        notif = Notification.objects.get(recipient=self.author, notification_type="new_follower")
        self.assertIn(self.consumer.username, notif.message)

        dup_res = self.client.post("/api/subscriptions/authors/subscribe/", payload, format="json")
        self.assertEqual(dup_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_work_and_notification(self):
        work = Work.objects.create(
            title="Luces y Sombras Urbanas",
            description="Cortometraje experimental sobre el ritmo diario de la ciudad.",
            author=self.author,
            work_type="video",
            status="published"
        )

        response = self.client.post("/api/subscriptions/works/subscribe/", {"work_id": work.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(SaveWork.objects.filter(consumer=self.consumer, work=work).exists())

        notif = Notification.objects.get(recipient=self.author, notification_type="new_saved_work")
        self.assertEqual(notif.work, work)

    def test_author_stats_counts(self):
        work = Work.objects.create(title="Suspendido", author=self.author, work_type="sculpture", status="published")
        SaveWork.objects.create(consumer=self.consumer, work=work)
        AuthorSubscription.objects.create(consumer=self.consumer, author=self.author)

        response = self.client.get(f"/api/subscriptions/authors/stats/?author_id={self.author.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["saved_works_count"], 1)
        self.assertEqual(response.data["subscribers_count"], 1)