from django.urls import path
from .views import WorkListCreateAPIView, ServeWorkFileAPIView, WorkDetailAPIView, ServeWorkResumeAPIView, ListWorksByAuthorAPIView, RecommendedWorksAPIView, BookGenresView,  BookLanguagesView, PaintTypeView, SculptureTypeView, MusicGenreView, VideoGenreView


app_name = 'works'

urlpatterns = [
    path('', WorkListCreateAPIView.as_view(), name='work_list_create'),
    path('<int:pk>/serve/', ServeWorkFileAPIView.as_view(), name='serve-work-file'),
    path('<int:pk>/', WorkDetailAPIView.as_view(), name='work_details'),
    path('<int:pk>/serve-resume/', ServeWorkResumeAPIView.as_view(), name='serve-work-resume'),
    path('authors/<int:author_id>/', ListWorksByAuthorAPIView.as_view(), name='author_work_list'),
    path('recommended/', RecommendedWorksAPIView.as_view(), name='recommended_works'),
    path('books/genres/', BookGenresView.as_view(), name='book-genres'),
    path('books/languages/', BookLanguagesView.as_view(), name='book-languages'),
    path('music/genres/', MusicGenreView.as_view(), name='music-genres'),
    path('video/genres/', VideoGenreView.as_view(), name='video-genres'),
    path('paint/types/', PaintTypeView.as_view(), name='paint-types'),
    path('sculpture/types/', SculptureTypeView.as_view(), name='sculpture-types'),
]
