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
   
]
