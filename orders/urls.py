from django.urls import path
from . import views

urlpatterns = [
    path('a;lkdf/checkout/order_checkout/', views.order_checkout, name='order_checkout'),
    path('checkout/order_confirmation/<int:order_id>/order/', views.order_confirmation, name='order_confirmation'),
    path('checkout/generate_invoice_pdf/<int:order_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('view/order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('cancel/cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('techtrove_admin/orders/admin_order_details/', views.admin_order_details, name='admin_order_details'),
    path('checkout/admin_order_update/<int:order_id>/', views.admin_order_detailed_view, name='admin_order_detailed_view'),
    path('generate/sales/report/', views.generate_sales_report, name='generate_sales_report'),
    path('generate/sales/report/pdf/sales_report/', views.generate_sales_report_pdf, name='generate_sales_report_pdf'),
    path('generate/sales/report/excel/', views.generate_sales_report_excel, name='generate_sales_report_excel'),
    path('generate/sales/report/excel/', views.payment_processing, name='payment_processing'),
]