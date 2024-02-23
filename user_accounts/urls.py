from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('user/verify/<int:uid>/', views.verify, name='verify'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout, name='logout'),
]