from django.db import models
from django.conf import settings
from users.models import User

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
        User, 
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
        User, 
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Cartera de {self.user.username} — Saldo: {self.points} puntos"
    
class AuthorSubscription(models.Model):
    consumer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='author_subscriptions'
    )
    
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    start_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('consumer', 'author')

    def __str__(self):
        return f"El consumidor {self.consumer.username} está suscrito al autor  {self.author.name}"
    
class SaveWork(models.Model):
    consumer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='saved_works'
    )
    
    work = models.ForeignKey(
        'works.Work',
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )

    start_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('consumer', 'work')

    def __str__(self):
        return f"El consumidor {self.consumer.username} ha guardado la obra  {self.work.title}"