from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, UserWallet, SaveWork
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
        
class SaveWorkSerializer(serializers.ModelSerializer):
    work_id = serializers.IntegerField(source='work.id', read_only=True)
    title = serializers.CharField(source='work.title', read_only=True)
    work_type = serializers.CharField(source='work.work_type', read_only=True)
    author_username = serializers.CharField(source='work.author.username', read_only=True)
    created_at = serializers.DateTimeField(source='work.created_at', read_only=True)

    class Meta:
        model = SaveWork
        fields = [
            'id',           
            'work_id',      
            'title',          
            'work_type',     
            'author_username', 
            'created_at',  
            'start_date'      
        ]
        read_only_fields = ['start_date']

