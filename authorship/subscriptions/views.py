from rest_framework import viewsets
from users.models import User
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import UserSubscription
from .models import AuthorSubscription
from .models import UserWallet
from .serializers import UserSubscriptionSerializer
from .serializers import UserWalletSerializer
from .serializers import SubscribedAuthorSerializer
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

class SubscriptionPlanListAPIView(APIView):
    def get(self, request):
        planes = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(planes, many=True)
        return Response(serializer.data)
    
class MySubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            subscription = UserSubscription.objects.get(user=request.user, active=True)
            serializer = UserSubscriptionSerializer(subscription)
            return Response(serializer.data)
        except UserSubscription.DoesNotExist:
            return Response({"detail": "No tienes una suscripción activa"}, status=404)
        
class MyWalletAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        wallet, created = UserWallet.objects.get_or_create(user=request.user)
        serializer = UserWalletSerializer(wallet)
        return Response(serializer.data)

        
class SubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            plan_id = request.data.get('plan_id')
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "No existe este plan"}, status=404)
        
        is_subscrited = UserSubscription.objects.filter(
            user=request.user, 
            active=True
        ).exists()

        if is_subscrited:
            return Response(
                {"detail": "Ya tienes una suscripción activa en tu cuenta."}, 
                status=400
            )

        try:
            plan_id = request.data.get('plan_id')
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "No existe este plan"}, status=404)

        wallet, created = UserWallet.objects.update_or_create(user=request.user)
        
        if wallet.points < plan.points:
            return Response({"detail": f"No tienes puntos suficientes para suscribirte al plan: {plan.name}"}, status=404)
        
        try:
            with transaction.atomic():
                wallet.points -= plan.points
                wallet.save()
                
            UserSubscription.objects.update_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timedelta(days=plan.duration_days),
                    'active': True
                }
            )
            
            return Response({"detail": f"Te has suscrito con éxito al {plan.name}"})
        
        except Exception as e:
            return Response({"error": "Hubo un error al procesar el pago de la suscripción."}, status=500)
    
class AuthorSubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):        
        consumer = request.user
        
        subscriptions = AuthorSubscription.objects.filter(consumer=consumer).select_related('author')
        authors = [sub.author for sub in subscriptions]
        
        serializer = SubscribedAuthorSerializer(authors, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        author_id = request.data.get('author_id')
        consumer = request.user
        
        try:
            author = User.objects.get(id=author_id, role="author")
        except User.DoesNotExist:
            return Response({"detail": "No existe este autor"}, status=404)
        
        if consumer.id == author.id:
            return Response({"detail": "No puedes suscribirte a ti mismo."}, status=400)

        is_subscrited = AuthorSubscription.objects.filter(
            consumer=consumer, 
            author=author
        ).exists()

        if is_subscrited:
            return Response(
                {"detail": "Ya estás suscrito a este autor."}, 
                status=400
            )
            
        AuthorSubscription.objects.create(
                consumer=consumer,
                author=author
            )
            
        return Response({"detail": f"Te has suscrito con éxito al autor {author.username}"})
    
    def delete(self, request):
        author_id = request.data.get('author_id')
        consumer = request.user
        
        try:
            author = User.objects.get(id=author_id, role="author")
        except User.DoesNotExist:
            return Response({"detail": "No existe este autor"}, status=404)
        
        if consumer.id == author.id:
            return Response({"detail": "No puedes desuscribirte a ti mismo."}, status=400)

        suscription = AuthorSubscription.objects.filter(
            consumer=consumer, 
            author=author
        ).first()

        if not suscription:
            return Response(
                {"detail": "No estás suscrito a este autor."}, 
                status=400
            )
            
        suscription.delete()
            
        return Response({"detail": f"Te has desuscrito con éxito al autor {author.username}"})
