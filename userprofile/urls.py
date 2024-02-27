from django.urls import path
from . import views


urlpatterns = [
    path('user_profile/', views.user_profile, name='user_profile'),
    path('update_user_data/', views.update_user_data, name='update_user_data'), 
    path('add_address/', views.add_address, name='add_address'),
    path('list_address/', views.list_address, name='list_address'),
    path('userprofile/edit_address/<pk>/', views.edit_address, name='edit_address'),
    path('userprofile/delete_address/<pk>/', views.delete_address, name='delete_address'),
    
]