from django.db import models
from django.conf import settings

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    points = models.IntegerField(default=15)
    description = models.TextField()
    duration_days = models.IntegerField(default=30)
    
    features_raw = models.TextField(
        help_text="Introduce las características separadas por comas.", 
        blank=True, 
        default=""
    )

    def __str__(self):
        return self.name
    
class UserSubscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    def is_valid(self):
        from django.utils import timezone
        return self.active and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
class UserWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Cartera de {self.user.username} — Saldo: {self.points} puntos"