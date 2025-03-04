from django.urls import path
from . import views
app_name = 'partner_api'

urlpatterns = [
    path('partner/<int:id>/', views.list_partner_by_id, name='partner-details'),
    path('partners/', views.list_partners, name='partner-list'),
    path('partners/create/', views.create_partner, name='partner-create'),
    path('partners/<int:id>/', views.update_partner, name='partner-update'),
    path('partners/<int:id>/delete/', views.delete_partner, name='partner-delete'),
]
