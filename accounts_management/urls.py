"""
URL configuration for accounts_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Accounts Management")

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/services/', include(('api.v1.services_api.urls'),namespace='services_api')),
    path('api/v1/users/', include(('api.v1.users_api.urls'),namespace='users_api')) , 
    path('api/v1/financials/', include(('api.v1.financials_api.urls'),namespace='financials_api')),
    path('api/v1/partner/', include(('api.v1.partner_api.urls'),namespace='partner_api')),
    path('',home,name='home'),

]
