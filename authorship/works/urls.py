from django.urls import path
from .views import WorkListCreateAPIView, ServeWorkFileAPIView, WorkDetailAPIView, ServeWorkResumeAPIView, ListWorksByAuthorAPIView


app_name = 'works'

urlpatterns = [
    path('', WorkListCreateAPIView.as_view(), name='work_list_create'),
    path('<int:pk>/serve/', ServeWorkFileAPIView.as_view(), name='serve-work-file'),
    path('<int:pk>/', WorkDetailAPIView.as_view(), name='work_details'),
    path('<int:pk>/serve-resume/', ServeWorkResumeAPIView.as_view(), name='serve-work-resume'),
    path('authors/<int:author_id>/', ListWorksByAuthorAPIView.as_view(), name='author_work_list'),
]
