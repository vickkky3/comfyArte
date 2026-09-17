from django.contrib import admin
from .models import Work, Book, Music, Video, Software, Paint, Sculpture


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'work_type',
        'license',
        'plan_required',
        'has_hash',
        'created_at'
    )
    list_filter = ('work_type', 'license', 'plan_required', 'created_at')
    search_fields = ('title', 'author__username', 'description', 'hash_security')
    autocomplete_fields = ('author', 'plan_required')
    readonly_fields = ('created_at', 'hash_security', 'has_binary_file', 'has_resume_file')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Identificación de la Obra', {
            'fields': ('title', 'author', 'work_type', 'description')
        }),
        ('Licencia y Monetización', {
            'fields': ('license', 'plan_required')
        }),
        ('Seguridad Criptográfica y Firma', {
            'classes': ('collapse',),
            'fields': ('hash_security',)
        }),
        ('Archivos Binarios Asociados', {
            'classes': ('collapse',),
            'fields': (
                'has_binary_file',
                'file_name',
                'file_type',
                'has_resume_file',
                'resume_name',
                'resume_type'
            )
        }),
        ('Auditoría', {
            'classes': ('collapse',),
            'fields': ('created_at',)
        }),
    )

    @admin.display(boolean=True, description='Certificada')
    def has_hash(self, obj):
        return bool(obj.hash_security)

    @admin.display(boolean=True, description='Archivo principal cargado')
    def has_binary_file(self, obj):
        return bool(obj.binary_file)

    @admin.display(boolean=True, description='Archivo resumen cargado')
    def has_resume_file(self, obj):
        return bool(obj.resume_file)


@admin.register(Book)
class BookAdmin(WorkAdmin):
    list_display = ('title', 'author', 'pages', 'isbn', 'genre', 'language', 'created_at')
    search_fields = ('title', 'author__username', 'isbn', 'genre')


@admin.register(Music)
class MusicAdmin(WorkAdmin):
    list_display = ('title', 'author', 'album', 'duration', 'genre', 'created_at')
    search_fields = ('title', 'author__username', 'album', 'genre')


@admin.register(Video)
class VideoAdmin(WorkAdmin):
    list_display = ('title', 'author', 'duration', 'genre', 'created_at')
    search_fields = ('title', 'author__username', 'genre')


@admin.register(Software)
class SoftwareAdmin(WorkAdmin):
    list_display = ('title', 'author', 'programming_language', 'repository_url', 'created_at')
    search_fields = ('title', 'author__username', 'programming_language')


@admin.register(Paint)
class PaintAdmin(WorkAdmin):
    list_display = ('title', 'author', 'type', 'height', 'weight', 'created_at')
    search_fields = ('title', 'author__username')


@admin.register(Sculpture)
class SculptureAdmin(WorkAdmin):
    list_display = ('title', 'author', 'type', 'height', 'weight', 'created_at')
    search_fields = ('title', 'author__username')