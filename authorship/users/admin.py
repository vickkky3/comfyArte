from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # tu modelo de usuario personalizado

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    # Puedes personalizar campos que quieres ver en admin
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'groups')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)