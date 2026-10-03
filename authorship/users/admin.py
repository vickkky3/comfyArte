from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification

INTEREST_LABELS = {
    'book': 'Libros',
    'music': 'Música',
    'video': 'Vídeos',
    'software': 'Software',
    'paint': 'Pintura',
    'sculpture': 'Escultura'
}

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
    
    readonly_fields = ('date_joined', 'last_login', 'display_interests', 'role', 'groups', 'user_permissions')

    fieldsets = (
        ('Usuario y contraseña', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'biography', 'display_interests')
        }),
        ('Rol en la Plataforma', {
            'fields': ('role',)
        }),
        ('Permisos y Accesos', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
        }),
        ('Fecha de Registro', {
            'classes': ('collapse',),
            'fields': ('date_joined',)
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Datos Adicionales', {
            'fields': ('role', 'email', 'interests', 'biography')
        }),
    )
    
    @admin.display(description='Intereses')
    def display_interests(self, obj):
        if not obj.interests:
            return "Sin intereses seleccionados"
        
        split_list = obj.interests.split(',')
            
        codes = []
        for item in split_list:
            item_limpio = item.strip()
            
            if item_limpio:
                codes.append(item_limpio)
                    
        translated = []
        for code in codes:

            if code in INTEREST_LABELS:
                spanish_name = INTEREST_LABELS[code]
                
            else:
                spanish_name = code.capitalize()
            
            translated.append(spanish_name)
        
        return ", ".join(translated)

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