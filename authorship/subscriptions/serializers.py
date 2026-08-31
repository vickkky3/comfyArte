from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, UserWallet
from users.models import User

class SubscriptionPlanSerializer(serializers.ModelSerializer):  
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        
class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.ReadOnlyField(source='plan.name')
    plan_points = serializers.ReadOnlyField(source='plan.points')
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_name', 'plan_points',
            'start_date', 'end_date', 'active'
        ]
        read_only_fields = ['user', 'start_date']
        

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = '__all__'
        read_only_fields = ['user', 'points']
        

class SubscribedAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'biography', 'role']

