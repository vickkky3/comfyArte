from django.db import models
from django.conf import settings
from users.models import User

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=200, verbose_name="Usuario")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Precio")
    points = models.IntegerField(default=15, editable=False, verbose_name="Puntos")
    description = models.TextField(verbose_name="Descripción")
    duration_days = models.IntegerField(default=30, verbose_name="Duración (días)")

    def save(self, *args, **kwargs):
        if self.price is not None:
            self.points = round(self.price * 10)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.points} pts)"
    
    class Meta:
        verbose_name = 'Plan de suscripción'
        verbose_name_plural = 'Planes de suscripción'
    
class UserSubscription(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='subscription', 
        verbose_name="Usuario"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, verbose_name="Plan")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inicio")
    end_date = models.DateTimeField(verbose_name="Fecha de fin")
    active = models.BooleanField(default=True, verbose_name="Activo")

    def is_valid(self):
        from django.utils import timezone
        return self.active and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    class Meta:
        verbose_name = 'Suscripción de usuario'
        verbose_name_plural = 'Suscripciones de usuario'
    
class UserWallet(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name="Usuario"
    )
    points = models.IntegerField(default=0, verbose_name="Puntos")
    
    def __str__(self):
        return f"Saldo de {self.user.username}: {self.points} puntos"
    
    class Meta:
        verbose_name = 'Cartera de puntos'
        verbose_name_plural = 'Carteras de puntos'
    
class AuthorSubscription(models.Model):
    consumer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='author_subscriptions', 
        verbose_name="Consumidor"
    )
    
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='subscribers', 
        verbose_name="Autor"
    )

    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inicio")
    
    class Meta:
        unique_together = ('consumer', 'author')

    def __str__(self):
        return f"El consumidor {self.consumer.username} está suscrito al autor  {self.author.username}"
    
    class Meta:
        verbose_name = 'Suscripción a autor'
        verbose_name_plural = 'Suscripciones a autores'
    
class SaveWork(models.Model):
    consumer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='saved_works', 
        verbose_name="Consumidor"
    )
    
    work = models.ForeignKey(
        'works.Work',
        on_delete=models.CASCADE,
        related_name='saved_by_users', 
        verbose_name="Obra"
    )

    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inicio")
    
    class Meta:
        unique_together = ('consumer', 'work')

    def __str__(self):
        return f"El consumidor {self.consumer.username} ha guardado la obra  {self.work.title}"
    
    class Meta:
        verbose_name = 'Obra guardada'
        verbose_name_plural = 'Obras guardadas'