from django.urls import path
from . import views

urlpatterns = [
    path('add_category/', views.add_category, name='addcategory'),
    path('edit_category/<pk>', views.edit_category, name='editcategory'),
    path('category_list/', views.category_list, name='categorylist'),
    path('<slug:category_slug>/', views.single_category, name='singlecat'),
]