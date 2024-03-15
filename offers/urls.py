from django.urls import path
from . import views

urlpatterns = [
    path('create_offer/', views.create_offer, name='create_offer'),
    path('list_offers/', views.list_offers, name='list_offers'),
    path('offers/edit/<pk>/<str:type>/offers/', views.offer_edit, name='offer_edit'),
    path('offers/delete/<pk>/<str:type>/offers/', views.delete_offer, name='delete_offer'),
]
