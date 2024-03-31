import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import paypalrestsdk
from django.db import transaction
from paypalrestsdk import Refund
from paypalrestsdk import Sale

from orders.models import Order, Wallet, Transaction, OrderProduct

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})

# Create your views here.

@transaction.atomic
def create_payment(request, order_id):
    order = Order.objects.get(order_id=order_id)
    grand_total = order.order_total

    try:
        order_products = OrderProduct.objects.filter(order=order)
    except OrderProduct.DoesNotExist:
        messages.warning(request, 'No orderitemsfound')
    
    products = []
    total = 0
    for order_product in order_products:
        if order_product.product.stock < order_product.quantity:
            products.append(order_product.product)
            total += order_product.product.price * order_product.quantity
            order.status = 'Cancelled'
            order.payment.status = 'Failed'
            order.payment.save()
            order.save()
            out_of_stock_product = order_product.product
            
            context = {
                    'order_products': order_products,
                    'products': products,
                    'order' : order,
                    'total' : total,
                    'out_of_stock_product' : out_of_stock_product,
                }
            
            messages.warning(request, f'{order_product.product.product_name} is only {order_product.product.stock} numbers available')
            return render(request, 'order_cancelled.html', context)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment', args=[order_id])),
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": str(grand_total),  # Total amount in USD (convert to string)
                    "currency": "USD",
                },
                "description": f"Payment for Order ID: {order_id}",
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'payment_failed.html')

@transaction.atomic
def execute_payment(request, order_id):
    payer_id = request.GET.get('PayerID')
    payment_id = request.GET.get('paymentId')

    order = Order.objects.get(order_id=order_id)

    try:
        order_products = OrderProduct.objects.filter(order=order)
    except OrderProduct.DoesNotExist:
        messages.warning(request, 'No orderitemsfound')
    
    products = []
    total = 0
    for order_product in order_products:
        if order_product.product.stock < order_product.quantity:
            products.append(order_product.product)
            total += order_product.product.price * order_product.quantity
            order.status = 'Cancelled'
            order.payment.status = 'Failed'
            order.payment.save()
            order.save()
            out_of_stock_product = order_product.product
            
            context = {
                    'order_products': order_products,
                    'products': products,
                    'order' : order,
                    'total' : total,
                    'out_of_stock_product' : out_of_stock_product,
                }
            
            messages.warning(request, f'{order_product.product.product_name} is only {order_product.product.stock} numbers available')
            return render(request, 'order_cancelled.html', context)

    payment = paypalrestsdk.Payment.find(payment_id)

    order_payment = order.payment

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        order.status = 'Accepted'
        order.save()
        order_payment.status = 'Completed'
        order_payment.transaction_id = payment.transactions[0].related_resources[0].sale.id
        order_payment.save()

        for order_product in order_products:
            order_product.product.stock -= order_product.quantity
            order_product.product.save()

        return render(request, 'payment_success.html')
    
    else:
        order_payment.status = 'Failed'
        order_payment.transaction_id = payment.transactions[0].related_resources[0].sale.id
        order_payment.save()
        return render(request, 'payment_failed.html')
    

@transaction.atomic
def process_refund(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        sale_id = order.payment.transaction_id

        sale = Sale.find(sale_id)

        refund = sale.refund({
            "amount": {
                "total": str(order.order_total),
                "currency": "USD",
            },
        })

        if refund.success():
            order.payment.status = 'Refunded'
            order.payment.save()

            # Check if a wallet exists for the user, create one if not
            wallet, created = Wallet.objects.get_or_create(user=request.user)

            # Only update wallet balance if creation wasn't necessary
            if not created:
                wallet.balance += order.order_total
                wallet.save()

                print(wallet.balance)

            Transaction.objects.create(
                wallet=wallet,
                order=order,
                amount=order.order_total,
                description=f'Refund for order {order.order_number}'
            )

            messages.success(request, 'Refund processed successfully!')
            return redirect('user_profile')
        else:
            messages.error(request, f'Refund failed: {refund.error.message}')
            return redirect('user_profile')

    except Order.DoesNotExist:
        # Handle order not found scenario
        messages.error(request, 'Order not found.')
        return redirect('user_profile')
    except Exception as e:
        # Catch generic exceptions for broader error handling
        messages.error(request, f'An error occurred: {e}')
        return redirect('user_profile')
    
def payment_failed(request):
    return render(request, 'payment_failed.html')
