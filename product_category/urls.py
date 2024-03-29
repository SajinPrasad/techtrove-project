from django.urls import path
from . import views

urlpatterns = [
    path('add_category/', views.add_category, name='addcategory'),
    path('edit_category/<pk>', views.edit_category, name='editcategory'),
    path('delete_category/<pk>', views.category_soft_delete, name='deletecategory'),
    path('category_list/', views.category_list, name='categorylist'),
    path('category/<slug:category_slug>/item/', views.single_category, name='singlecat'),
]