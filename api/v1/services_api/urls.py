from django.urls import path
from . import views

app_name = 'services_api'

urlpatterns = [
    # Category CRUD
    path('categories/', views.category_list, name='category_list'),                # List all categories
    path('categories/create/', views.category_create, name='category_create'),     # Create a new category
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),   # Retrieve a category
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),  # Update a category
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),  # Delete a category

    # Service CRUD under a specific category
    path('services/', views.services, name='service_list'),
    path('categories/<int:category_id>/services/', views.service_list, name='service_list'),  # List services in a category
    path('categories/<int:category_id>/services/create/', views.create_service, name='create_service'),  # Create a service in a category
    path('categories/<int:category_id>/services/<int:service_id>/update/', views.update_service, name='update_service'),  # Update a service in a category
    path('services/<int:service_id>/delete/', views.delete_service, name='delete_service'),  
    
]
