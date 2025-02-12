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

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/customers/', include(('api.v1.customers_api.urls'),namespace='customers_api')),
    # path('api/v1/main_admin/', include(('api.v1.main_admin_api.urls'),namespace='main_admin_api')),
    # path('api/v1/reports/', include(('api.v1.reports_api.urls'),namespace='reports_api')),
    path('api/v1/services/', include(('api.v1.services_api.urls'),namespace='services_api')),
    path('api/v1/users/', include(('api.v1.users_api.urls'),namespace='users_api')) , 
    path('api/v1/dashboard/', include(('api.v1.dashboard_api.urls'),namespace='dashboard_api')) , 
    path('api/v1/financials/', include(('api.v1.financials_api.urls'),namespace='financials_api')),

]
