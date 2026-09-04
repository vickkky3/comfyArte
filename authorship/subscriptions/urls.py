from django.urls import path
from .views import SubscriptionPlanListAPIView, MySubscriptionAPIView, SubscribeAPIView, MyWalletAPIView, AuthorSubscribeAPIView, SaveWorkAPIView, AuthorStatsAPIView

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', SubscriptionPlanListAPIView.as_view(), name='plan_list'),
    path('me/', MySubscriptionAPIView.as_view(), name='my_subscription'),
    path('subscribe/', SubscribeAPIView.as_view(), name='subscribe_action'),
    path('points/', MyWalletAPIView.as_view(), name='my_wallet'),
    path('authors/subscribe/', AuthorSubscribeAPIView.as_view(), name='author_subscription'),
    path('works/subscribe/', SaveWorkAPIView.as_view(), name='work_subscription'),
    path('authors/stats/', AuthorStatsAPIView.as_view(), name='author-stats'),

]