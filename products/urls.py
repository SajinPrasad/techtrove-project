from django.urls import path
from . import views


urlpatterns = [
    path('add_product/', views.add_product, name='addproduct'),
    path('edit_product/<pk>', views.edit_product, name='editproduct'),
    path('delete_product/<pk>', views.soft_delete_product, name='deleteproduct'),
    path('list_product/', views.list_product, name='listproduct'),
    path('product_detail/<str:cat_slug>/<str:prod_slug>/techtrove/', views.single_product_admin, name='singleproductadmin'),
    path('product/update/<int:pk>/product/', views.ProductUpdateView.as_view(), name='product_update'),
]