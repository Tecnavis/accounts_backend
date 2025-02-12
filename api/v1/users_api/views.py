from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from .serializers import LoginSerializer, UserListSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required as admin_required

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


@admin_required  # Only existing admins can create new admins
def create_admin(request):
    if request.method == 'POST':
        # Form validation and admin creation logic
        new_admin = CustomUser.objects.create_admin(
            email=request.POST['email'],
            username=request.POST['username'],
            password=request.POST['password']
        )
        return redirect('admin_list')
    return render(request, 'create_admin.html')  



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
def get_user_profile(request):
    user = request.user
    serializer = UserListSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


     
