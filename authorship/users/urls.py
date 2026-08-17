from django.urls import path
from .views import RegisterAPIView, UserDataAPIView, AuthorListAPIView
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token 

app_name = 'users'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('me/', UserDataAPIView.as_view(), name='api_user_data'),
    path('authors/', AuthorListAPIView.as_view(), name='api_author_list'),
    path('login/', obtain_auth_token, name='api_token_auth'), 
    path('logout/', auth_views.LogoutView.as_view(), name='api_logout'),
    path('<int:pk>/', WorkDetailAPIView.as_view(), name='author_details'),
]