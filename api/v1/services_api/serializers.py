from rest_framework import serializers
from services.models import Category, Service


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active']         


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name') 
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Allow editing category
    offer_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    class Meta:
        model = Service
        exclude = ['service_type']  
        
    
        