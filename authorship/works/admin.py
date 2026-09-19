from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponse, Http404
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from .models import Work, Book, Music, Video, Software, Paint, Sculpture
from users.models import Notification


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'work_type',
        'status',
        'download_binary_link',
        'download_resume_link',
        'created_at'
    )
    list_filter = ('status', 'work_type', 'license', 'plan_required', 'created_at')
    search_fields = ('title', 'author__username', 'description', 'rejection_reason')
    autocomplete_fields = ('author', 'plan_required')
    readonly_fields = (
        'created_at', 
        'hash_security', 
        'has_binary_file', 
        'has_resume_file', 
        'download_binary_link',
        'download_resume_link',
        'rejection_reason',
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    actions = ['manual_approve_work', 'manual_reject_work']

    fieldsets = (
        ('Identificación de la Obra', {
            'fields': ('title', 'author', 'work_type', 'description')
        }),
        ('Estado de Revisión y Validación', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Licencia y Monetización', {
            'fields': ('license', 'plan_required')
        }),
        ('Seguridad Criptográfica y Firma', {
            'classes': ('collapse',),
            'fields': ('hash_security',)
        }),
        ('Archivos Binarios Asociados', {
            'fields': (
                'download_binary_link',
                'has_binary_file',
                'file_name',
                'file_type',
                'download_resume_link',
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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:work_id>/download/binary/',
                self.admin_site.admin_view(self.download_binary),
                name='work-download-binary',
            ),
            path(
                '<int:work_id>/download/resume/',
                self.admin_site.admin_view(self.download_resume),
                name='work-download-resume',
            ),
        ]
        return custom_urls + urls
    
    def download_binary(self, request, work_id):
        work = get_object_or_404(Work, pk=work_id)
        if not work.binary_file:
            raise Http404("La obra no contiene archivo principal.")

        filename = work.file_name or f"obra_{work.id}"
        content_type = work.file_type or 'application/octet-stream'

        response = HttpResponse(work.binary_file, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def download_resume(self, request, work_id):
        work = get_object_or_404(Work, pk=work_id)
        if not work.resume_file:
            raise Http404("La obra no contiene archivo de muestra.")

        filename = work.resume_name or f"resumen_{work.id}"
        content_type = work.resume_type or 'application/octet-stream'

        response = HttpResponse(work.resume_file, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def download_binary_link(self, obj):
        if obj and obj.binary_file:
            url = reverse('admin:work-download-binary', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Descargar archivo principal</a>', url)
        return "Sin archivo"
    download_binary_link.short_description = "Archivo principal"

    def download_resume_link(self, obj):
        if obj and obj.resume_file:
            url = reverse('admin:work-download-resume', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Descargar muestra</a>', url)
        return "Sin muestra"
    download_resume_link.short_description = "Muestra / Resumen"
    
    @admin.action(description="Aprobar obras seleccionadas (Notificar al autor)")
    def manual_approve_work(self, request, queryset):
        approved_works = 0
        for work in queryset:
            work.status = 'approved'
            work.save()

            Notification.objects.create(
                recipient=work.author,
                work=work,
                notification_type='approved_work',
                message=f"Tu obra '{work.title}' ha sido revisada y aprobada por el equipo de administración."
            )
            approved_works += 1
            
        self.message_user(request, f"{approved_works} obras aprobadas y sus autores han sido notificados.")

    @admin.action(description="Rechazar obras definitivamente")
    def manual_reject_work(self, request, queryset):
        reject_works = 0
        for work in queryset:
            work.status = 'rejected_manual'
            work.save()

            Notification.objects.create(
                recipient=work.author,
                work=work,
                notification_type='rejected_work',
                message=f"Tras la revisión manual, tu obra '{work.title}' no cumple con las directrices de la plataforma."
            )
            reject_works += 1
            
        self.message_user(request, f"{reject_works} obras rechazadas definitivamente.")


@admin.register(Book)
class BookAdmin(WorkAdmin):
    list_display = ('title', 'author', 'status', 'pages', 'isbn', 'genre', 'language', 'download_binary_link', 'created_at')
    search_fields = ('title', 'author__username', 'isbn', 'genre')


@admin.register(Music)
class MusicAdmin(WorkAdmin):
    list_display = ('title', 'author', 'status', 'album', 'duration', 'genre', 'download_binary_link', 'created_at')
    search_fields = ('title', 'author__username', 'album', 'genre')


@admin.register(Video)
class VideoAdmin(WorkAdmin):
    list_display = ('title', 'author', 'status', 'duration', 'genre', 'download_binary_link', 'created_at')
    search_fields = ('title', 'author__username', 'genre')


@admin.register(Software)
class SoftwareAdmin(WorkAdmin):
    list_display = ('title', 'author', 'status', 'programming_language', 'repository_url', 'download_binary_link', 'created_at')
    search_fields = ('title', 'author__username', 'programming_language')


@admin.register(Paint)
class PaintAdmin(WorkAdmin):
    list_display = ('title', 'author', 'status', 'type', 'height', 'weight', 'download_binary_link', 'created_at')
    search_fields = ('title', 'author__username')


@admin.register(Sculpture)
class SculptureAdmin(WorkAdmin):
    list_display = ('title', 'author', 'status', 'type', 'height', 'weight', 'download_binary_link', 'created_at')
    search_fields = ('title', 'author__username')