from django.urls import path
from .import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:cart_item_id>/', views.update_cart_item, name='update_cart'),
    path('delete_cart_item/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
]
