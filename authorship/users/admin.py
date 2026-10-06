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
        'is_superuser',
        'date_joined'
    )
    
    readonly_fields = ('date_joined', 'last_login', 'role', 'groups', 'display_interests',)
    
    def get_role_display(self, obj):
        if obj.is_superuser:
            return "Administrador"
        if getattr(obj, 'role', None) == 'author' or obj.groups.filter(name__iexact='Author').exists():
            return "Autor"
        
        return "Consumidor"
    
    get_role_display.short_description = "Rol"

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        fieldsets = [
            (None, {'fields': ('username', 'password')}),
            ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
            ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
            ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
        ]

        is_admin = obj.is_superuser or obj.is_staff or getattr(obj, 'role', '') == 'admin'
        is_author = getattr(obj, 'role', '') == 'author' or obj.groups.filter(name__iexact='Author').exists()

        if is_admin:
            pass
        
        elif is_author:
            fieldsets.insert(2, ('Perfil de Autor', {
                'fields': ('biography',), 
            }))
            
        else:
            fieldsets.insert(2, ('Preferencias de Consumidor', {
                'fields': ('display_interests',), 
            }))

        return fieldsets
    
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
    list_display = ('recipient', 'sender', 'notification_type', 'message', 'work', 'created_at')
    list_filter = ('notification_type', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'message', 'work__title')
    autocomplete_fields = ('recipient', 'sender', 'work')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def message(self, obj):
        return obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
    
    message.short_description = 'Mensaje'