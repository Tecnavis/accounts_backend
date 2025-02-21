from django.urls import path
from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView,TokenVerifyView


app_name = 'users_api'


urlpatterns = [

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.login_user, name='login'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/',views.get_user_profile,name='user_list'),
    path("users/<int:id>/",views.get_user_profile_by_id,name='user-detail'),
    path('staffs/', views.list_staff_users, name='list_staff_users'),
    path('staffs/<int:id>/', views.update_staff_user, name='update_staff_user'),
    path('staffs/revoke/<int:id>/', views.revoke_staff_user, name='revoke_staff_user'),
    path('staffs/<int:id>/delete/', views.delete_staff_user, name='delete_staff_user'),
    path('staffs/create/', views.create_staff_user, name='create_staff_user'),
    path('admin/create/', views.create_admin_user, name='create_admin_user'),

   
]
