from django.contrib import admin
from .models import (
    SubscriptionPlan,
    UserSubscription,
    UserWallet,
    AuthorSubscription,
    SaveWork
)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'points', 'duration_days', 'subscribers_count')
    list_filter = ('duration_days',)
    search_fields = ('name', 'description')
    ordering = ('price',)
    readonly_fields = ('points',)

    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description')
        }),
        ('Tarificación y Recompensas', {
            'fields': ('price', 'points', 'duration_days')
        }),
        ('Prestaciones', {
            'fields': ('features_raw',)
        }),
    )

    def subscribers_count(self, obj):
        return obj.usersubscription_set.count()
    subscribers_count.short_description = 'Suscripciones activas'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active_status')
    list_filter = ('active', 'plan', 'start_date', 'end_date')
    search_fields = ('user__username', 'user__email', 'plan__name')
    autocomplete_fields = ('user', 'plan')
    readonly_fields = ('start_date',)
    date_hierarchy = 'start_date'

    actions = ['cancel_subscriptions', 'activate_subscriptions']

    @admin.display(boolean=True, description='Activa')
    def is_active_status(self, obj):
        return obj.is_valid()

    @admin.action(description='Desactivar suscripciones seleccionadas')
    def cancel_subscriptions(self, request, queryset):
        filas = queryset.update(active=False)
        self.message_user(request, f"{filas} suscripciones marcadas como inactivas.")

    @admin.action(description='Activar suscripciones seleccionadas')
    def activate_subscriptions(self, request, queryset):
        filas = queryset.update(active=True)
        self.message_user(request, f"{filas} suscripciones reactivadas.")


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')
    search_fields = ('user__username', 'user__email')
    autocomplete_fields = ('user',)
    ordering = ('-points',)


@admin.register(AuthorSubscription)
class AuthorSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'author', 'start_date')
    search_fields = ('consumer__username', 'author__username')
    autocomplete_fields = ('consumer', 'author')
    date_hierarchy = 'start_date'


@admin.register(SaveWork)
class SaveWorkAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'work_title', 'work_type', 'start_date')
    list_filter = ('work__work_type', 'start_date')
    search_fields = ('consumer__username', 'work__title')
    autocomplete_fields = ('consumer', 'work')
    date_hierarchy = 'start_date'

    def work_title(self, obj):
        return obj.work.title
    work_title.short_description = 'Obra guardada'

    def work_type(self, obj):
        return obj.work.get_work_type_display() if hasattr(obj.work, 'get_work_type_display') else obj.work.work_type
    work_type.short_description = 'Tipo'