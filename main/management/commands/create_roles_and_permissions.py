from django.core.management.base import BaseCommand
from users.models import CustomUser,UserRoles
from rest_framework.permissions import BasePermission


from django.core.management.base import BaseCommand
from users.models import CustomUser, UserRoles

class Command(BaseCommand):
    help = "Create default Super Admin, Admin, and Staff users"

    def handle(self, *args, **kwargs):
        users_to_create = [
            {
                "email": "superadminn@gmail.com",
                "username": "superadmin",
                "password": "superadmin@1234",
                "role": UserRoles.SUPER_ADMIN,
                "is_staff": True,
                "is_superuser": True
            },
            {
                "email": "adminn@gmail.com",
                "username": "admin",
                "password": "admin@1234",
                "role": UserRoles.ADMIN,
                "is_staff": True,
                "is_superuser": False
            },
            {
                "email": "staff@gmail.com",
                "username": "staff",
                "password": "staff@1234",
                "role": UserRoles.STAFF,
                "is_staff": False,
                "is_superuser": False
            }
        ]

        for user_data in users_to_create:
            if not CustomUser.objects.filter(email=user_data["email"]).exists():
                if user_data["role"] == UserRoles.SUPER_ADMIN:
                    user = CustomUser.objects.create_superuser(
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"]
                    )
                else:
                    user = CustomUser.objects.create_user(
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"],
                        role=user_data["role"],
                        is_staff=user_data["is_staff"]
                    )

                self.stdout.write(self.style.SUCCESS(f"✅ {user_data['role'].capitalize()} user created: {user.email}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ {user_data['role'].capitalize()} user already exists: {user_data['email']}"))


class IsMainAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRoles.SUPER_ADMIN

class IsSecondaryAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and str(request.user.role).upper() == str(UserRoles.ADMIN).upper()
        
class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRoles.STAFF
    

    