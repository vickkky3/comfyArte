from django.urls import path
from .views import SubscriptionPlanListAPIView, MySubscriptionAPIView, SubscribeAPIView, MyWalletAPIView, AuthorSubscribeAPIView

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', SubscriptionPlanListAPIView.as_view(), name='plan_list'),
    path('me/', MySubscriptionAPIView.as_view(), name='my_subscription'),
    path('subscribe/', SubscribeAPIView.as_view(), name='subscribe_action'),
    path('points/', MyWalletAPIView.as_view(), name='my_wallet'),
    path('authors/subscribe/', AuthorSubscribeAPIView.as_view(), name='author_subscription'),
]