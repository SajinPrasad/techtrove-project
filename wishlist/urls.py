from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/delete/<int:pk>/product/', views.delete_item_wishlist, name='delete_item_wishlist'),
    # path('wishlist/update/<int:pk>/product/', views.update_wishlist, name='update_wishlist'),
]