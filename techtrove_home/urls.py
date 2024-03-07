from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landingpage'),
    path('userhome/', views.user_home, name='userhome'),
    path('<str:category_slug>/<str:product_slug>/', views.single_product, name='singleproduct'),
    path('category_filter/<int:cat_id>/shop/', views.category_filter_shop, name='category_filter_shop'),
    path('shop_view/', views.shop_view, name='shop_view'),
    path('product/category/filter/', views.product_filter, name='product_filter'),
    path('search_products/', views.search_products, name='search_products'),
]
