from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth import authenticate


CustomUser = get_user_model() 

class CustomUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, required=True)  # Add password field

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'contact_number', 'employee_id', 'is_staff','is_active']
        extra_kwargs = {'is_staff': {'read_only': True},
                        
                        'is_active': {'required': False}
                        }

    def create(self, validated_data):
        password = validated_data.pop('password', None) 
        validated_data['is_staff'] = True  
       
        
        user = CustomUser.objects.create_user(**validated_data) 
        
        if password:
            user.set_password(password) 
            user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            print(user,"user??")

            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs['user'] = user
        return attrs

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','email','role','is_active','is_staff','date_joined','contact_number','employee_id']
        read_only_fields = ['id','date_joined']

   