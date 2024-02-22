from django.urls import path
from . import views

urlpatterns = [
    path('adminhome/', views.adminhome, name='adminhome'),
    path('adminlogin/', views.admin_login, name='adminlogin'),
    path('adminlogout/', views.admin_logout, name='adminlogout'),
]
