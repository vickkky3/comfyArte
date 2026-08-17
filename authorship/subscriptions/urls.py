from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.SubscriptionPlanListAPIView.as_view(), name='plan_list'),
    path('me/', views.MySubscriptionAPIView.as_view(), name='my_subscription'),
    path('subscribe/', views.SubscribeAPIView.as_view(), name='subscribe_action'),
    path('points/', views.MyWalletAPIView.as_view(), name='my_wallet'),
]