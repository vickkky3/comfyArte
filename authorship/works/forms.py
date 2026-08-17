from django import forms
from works.models import Book, Music, Video, Software, Paint, Sculpture

class BaseWorkForm(forms.ModelForm):
    file_upload = forms.FileField(required=False, label="Subir archivo adjunto")
    resume_upload = forms.FileField(required=False, label="Subir archivo adjunto")
    
    class Meta:
        fields = ['title', 'description', 'file_upload', 'resume_upload']

class BookForm(BaseWorkForm):    
    class Meta:
        model = Book
        fields = BaseWorkForm.Meta.fields + ['pages', 'isbn', 'language', 'genre',]

class MusicForm(BaseWorkForm):    
    class Meta:
        model = Music
        fields = BaseWorkForm.Meta.fields + ['duration', 'album', 'genre',]

class VideoForm(BaseWorkForm):    
    class Meta:
        model = Video
        fields = BaseWorkForm.Meta.fields + ['duration', 'genre',]

class SoftwareForm(BaseWorkForm):    
    class Meta:
        model = Software
        fields = BaseWorkForm.Meta.fields + ['programming_language', 'repository_url', 'documentation_url',]

class PaintForm(BaseWorkForm):
    class Meta:
        model = Paint
        fields = BaseWorkForm.Meta.fields + ['height', 'weight', 'type',]

class SculptureForm(BaseWorkForm):
    class Meta:
        model = Sculpture
        fields = BaseWorkForm.Meta.fields + ['height', 'weight', 'type',]