from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'is_staff',
        'date_joined'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'interests')
    ordering = ('-date_joined',)
    
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        ('Identificación y Cuenta', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'biography', 'interests')
        }),
        ('Rol de Plataforma', {
            'fields': ('role',)
        }),
        ('Permisos y Accesos', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas de Auditoría', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Datos Adicionales', {
            'fields': ('role', 'email', 'interests', 'biography')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'message_snippet', 'work', 'created_at')
    list_filter = ('notification_type', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'message', 'work__title')
    autocomplete_fields = ('recipient', 'sender', 'work')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def message_snippet(self, obj):
        return obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
    message_snippet.short_description = 'Mensaje'