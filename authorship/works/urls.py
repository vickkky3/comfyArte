from django.urls import path
from . import views

app_name = 'works'

urlpatterns = [
    path('', views.WorkListCreateAPIView.as_view(), name='work_list_create'),
    path('<int:pk>/serve/', views.ServeWorkFileAPIView.as_view(), name='serve-work-file'),
    path('<int:pk>/', views.WorkDetailAPIView.as_view(), name='work_details'),
    path('<int:pk>/serve-resume/', views.ServeWorkResumeAPIView.as_view(), name='serve-work-resume'),
]
