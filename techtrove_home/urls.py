from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landingpage'),
    path('userhome/', views.user_home, name='userhome'),
    path('<str:category_slug>/<str:product_slug>/', views.single_product, name='singleproduct'),
]
