from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.models import CustomUser, UserRoles
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from .serializers import LoginSerializer, UserListSerializer,CustomUserSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required as admin_required
from main.management.commands.create_roles_and_permissions import IsMainAdmin,IsSecondaryAdmin

import logging
logger = logging.getLogger(__name__)



# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register_user(request):
#     """
#     Register Secondary Admin, Customer, or Vendor based on the role passed.
#     No authentication is required for registration.
#     """
#     print(f"Request data: {request.data}")
    
#     role_name = request.data.get('role')
#     print(f"Received role: {role_name}")
#     valid_roles = ['main_admin','staffs', 'customer', 'vendor']
#     if role_name not in valid_roles:
#         return Response({"detail": f"Invalid role specified. Only {', '.join(valid_roles)} are allowed."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         role = Role.objects.get(name=role_name)
#         request.data['role'] = role.id
#     except Role.DoesNotExist:
#         return Response({"detail": f"Role '{role_name}' does not exist in the database."}, status=status.HTTP_400_BAD_REQUEST)

#     serializer = UserRegistrationSerializer(data=request.data)

#     if serializer.is_valid():
#         user = serializer.save()
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)

#         return Response(
#             {
#                 'detail': f'{role_name.capitalize()} registered successfully!',
#                 'user_id': user.id,
#                 'access_token': access_token,
#                 'refresh_token': str(refresh),
#             },
#             status=status.HTTP_201_CREATED
#         )
#     else:
#         print(f"Serializer errors: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login endpoint for users
    """
    serializer = LoginSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print(user,"user")
        refresh = RefreshToken.for_user(user)
        response_data = {
            'detail': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except serializers.ValidationError as e:      
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request):
    user = request.user
    serializer = UserListSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile_by_id(request, id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserListSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsSecondaryAdmin]) 
def create_staff_user(request):
    serializer = CustomUserSerializer(data=request.data)
    
    if serializer.is_valid():
        password = serializer.validated_data.pop('password', None)  
        user = serializer.save(is_staff=True)
        
        if password:
            user.set_password(password)  
            user.save()
        
        return Response(
            {"message": "Staff user created successfully"},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsMainAdmin])  
def create_admin_user(request):
    serializer = CustomUserSerializer(data=request.data)
    
    if serializer.is_valid():
        password = serializer.validated_data.pop('password', None)  
        
        user = serializer.save(
            role=UserRoles.ADMIN, 
            is_staff=True, 
            is_superuser=False  
        )

        if password:
            user.set_password(password)  
            user.save()
        
        return Response(
            {"message": "Admin user created successfully"},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_staff_users(request):
    staff_users = CustomUser.objects.filter(is_staff=True)
    serializer = UserListSerializer(staff_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# update staff user
@api_view(['PUT'])
@permission_classes([IsSecondaryAdmin])  
def update_staff_user(request, id):
    try:
        staff_user = CustomUser.objects.get(pk=id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomUserSerializer(staff_user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@permission_classes([IsMainAdmin,IsSecondaryAdmin])  
def revoke_staff_user(request, id):
    
    staff_user = CustomUser.objects.get(id=id)
   
    serializer = CustomUserSerializer(staff_user, data=request.data, partial=True)  # ✅ Allow partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsMainAdmin,IsSecondaryAdmin])  
def delete_staff_user(request, id):
    staff_user = CustomUser.objects.get(pk=id)
    staff_user.is_deleted = True
    staff_user.save()
    return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)