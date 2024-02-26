from django.urls import path
from . import views


urlpatterns = [
    path('add_product/', views.add_product, name='addproduct'),
    path('edit_product/<pk>', views.edit_product, name='editproduct'),
    path('delete_product/<pk>', views.soft_delete_product, name='deleteproduct'),
    path('list_product/', views.list_product, name='listproduct'),
    path('<str:category_slug>/<str:product_slug>/', views.single_product_admin, name='singleproductadmin'),
]