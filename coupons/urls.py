from django.urls import path
from . import views

urlpatterns = [
    path('apply_coupons/', views.apply_coupons, name='apply_coupons'),
    path('coupon/remove_coupons/<str:coupon_applied>/remove/', views.remove_coupons, name='remove_coupons'),
    path('add_coupons/', views.add_coupons, name='add_coupons'),
    path('list_coupons/', views.list_coupons, name='list_coupons'),
    path('edit/coupons/<pk>/coupon/', views.edit_coupons, name='edit_coupons'),
    path('delete/coupons/<pk>/coupon/', views.delete_coupons, name='delete_coupons'),
]
