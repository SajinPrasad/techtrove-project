from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landingpage'),
    path('userhome/', views.user_home, name='userhome'),
    path('single_product/', views.single_product, name='singleproduct'),
]
