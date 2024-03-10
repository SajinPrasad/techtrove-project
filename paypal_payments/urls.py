from django.urls import path
from . import views

urlpatterns = [
    path('checkout/create-payment/<int:order_id>/order/', views.create_payment, name='create_payment'),
    path('checkout/execute-payment/<int:order_id>/order/', views.execute_payment, name='execute_payment'),
    path('checkout/process-refund/<int:order_id>/order/', views.process_refund, name='process_refund'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
]