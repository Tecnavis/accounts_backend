from django.urls import path
from . import views
app_name = 'partner_api'

urlpatterns = [
    path('partners/', views.list_partners, name='partner-list'),
    path('partners/create/', views.create_partner, name='partner-create'),
    path('partners/<int:pk>/', views.update_partner, name='partner-update'),
    path('partners/<int:pk>/', views.delete_partner, name='partner-delete'),
]