from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from django.middleware.csrf import get_token
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from cart.models import Cart, CartItem
from .forms import OrderForm, OrderStatusForm, PaymentStatusForm
from .models import Order, Payment, OrderProduct, Wallet
from userprofile.models import Address
from userprofile.forms import AddressForm

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def order_checkout(request):
    user            = request.user
    wallet_msg      = None
    wallet, create  = Wallet.objects.get_or_create(user=user)

    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        messages.info(request, 'Your cart is empty')
        return redirect('cart')
    
    for cart_item in cart_items:
        item = cart_item.product

        if not item.is_available:
            messages.info(request, f'{item.product_name} is not available right now')
            return redirect('cart')
    
    products = []
    products_with_quantity = {}

    for cart_item in cart_items:
        product     = cart_item.product
        quantity    = cart_item.quantity
        products_with_quantity[product] = quantity

    try:
        primary_address = Address.objects.get(user=user, is_primary=True)
    except Address.DoesNotExist:
        primary_address = None

    count = cart_items.count()

    grand_total = Decimal(0)
    total       = Decimal(0)
    tax         = Decimal(0)
    shipping_fee = Decimal(30)

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity

    tax = (2 * total / 100)
    grand_total = total + tax + shipping_fee

    if count == 0:
        messages.info(request, 'Cart is empty, add items from the shop.')
        return redirect('shop_view')

    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        a_form = AddressForm()

        if form.is_valid():
            data    = Order()

            data.user           = user
            data.first_name     = form.cleaned_data['first_name']
            data.last_name      = form.cleaned_data['last_name']
            data.email          = form.cleaned_data['email']
            data.phone          = form.cleaned_data['phone']
            data.order_note     = form.cleaned_data['order_note']
            # save_address        = form.cleaned_data.get('save_address', False)

            save_address        = request.POST.get('save-address', '')
            diff_address        = request.POST.get('diff-address', '')
            selected_address_id = form.cleaned_data['address']

            if selected_address_id:
                # selected_address = Address.objects.get(pk=selected_address_id)
                data.address        = selected_address_id
                selected_address    = str(f'{selected_address_id.address_line}, {selected_address_id.street_name}, {selected_address_id.city}, {selected_address_id.state}, {selected_address_id.country}, {selected_address_id.country}, {selected_address_id.zip_code}')
                
                data.billing_address = selected_address

            elif diff_address:
                address_line        = request.POST.get('address_line')
                street_name         = request.POST.get('street_name')
                city                = request.POST.get('city')
                state               = request.POST.get('state')
                country             = request.POST.get('country')
                zip_code            = request.POST.get('zip_code')

                data.billing_address = str(f'{address_line}, {street_name}, {city}, {state}, {country}, {zip_code}')

                if save_address:
                    new_address         = Address.objects.create(
                        user            = user,
                        address_line    = request.POST.get('address_line'),
                        street_name     = request.POST.get('street_name'),
                        city            = request.POST.get('city'),
                        state           = request.POST.get('state'),
                        country         = request.POST.get('country'),
                        zip_code        = request.POST.get('zip_code'),
                    )

                    data.address = new_address
            
            data.order_total    = grand_total
            data.tax            = tax
            data.shipping_fee   = shipping_fee
            data.save()

            data.order_number = f"{data.created_at.strftime('%Y%m%d')}-{data.order_id}"

            payment_method = request.POST.get('payment-method', '')

            terms_and_conditions   = request.POST.get('accept-terms', '')

            if payment_method == 'cash'and terms_and_conditions:
                payment = Payment.objects.create(
                    user            = user,
                    payment_method  = 'Cash on delivery',
                    amount          = grand_total,
                    status          = 'Pending'
                )
                data.payment        = payment
                data.status         = 'Pending'
                data.save()

                for cart_item in cart_items:
                    OrderProduct.objects.create(
                        order=data,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                    )
                
                cart.delete()

                return HttpResponseRedirect(reverse('order_confirmation', args=[data.order_id]))
            
            elif payment_method == 'paypal'and terms_and_conditions:
                payment = Payment.objects.create(
                    user            = user,
                    payment_method  = 'paypal',
                    amount          = grand_total,
                    status          = 'Pending'
                )
                data.payment        = payment
                data.status         = 'Pending'
                data.save()

                for cart_item in cart_items:
                    OrderProduct.objects.create(
                        order=data,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                    )

                cart.delete()

                return HttpResponseRedirect(reverse('order_confirmation', args=[data.order_id]))
            
            elif payment_method == 'Wallet'and terms_and_conditions:

                if wallet.balance >= grand_total:
                    payment = Payment.objects.create(
                        user            = user,
                        payment_method  = 'Wallet',
                        amount          = grand_total,
                        status          = 'Pending'
                    )

                    data.payment        = payment
                    data.status         = 'Pending'
                    data.save()

                    for cart_item in cart_items:
                        OrderProduct.objects.create(
                            order       = data,
                            product     = cart_item.product,
                            quantity    = cart_item.quantity,
                        )
                    
                    cart.delete()

                    return HttpResponseRedirect(reverse('order_confirmation', args=[data.order_id]))
                
                else:
                    wallet_msg = f'Your wallet balance is only ₹{wallet.balance}, so chose other options.'

    else:
        form = OrderForm(user=request.user)
        if primary_address:
            a_form = AddressForm(instance=primary_address)
        else:
            a_form = AddressForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'a_form': a_form,
        'tax' : tax,
        'total' : total,
        'products' : products,
        'shippping_fee' : shipping_fee,
        'products_with_quantity': products_with_quantity,
        'csrf_token': get_token(request),
        'wallet_msg' : wallet_msg,
        'wallet' : wallet,
    }

    return render(request, 'checkout.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def order_confirmation(request, order_id):
    order = Order.objects.get(order_id=order_id)
    
    try:
        # Try to get the OrderProduct object using get()
        order_products = OrderProduct.objects.filter(order_id=order_id)

        if not order_products:
            raise Http404("Order product not found")
    except OrderProduct.DoesNotExist:
        # If no object is found, raise a specific error message
        raise Http404("Order product not found")

    products = [product.product for product in order_products]

    for order_product in order_products:
        total = order_product.quantity * order_product.product.price

    for item in products:
        if not item.is_available:
            messages.success(request, f'{item.product_name} is not available right now.')
            return redirect('order_checkout')
        
    context = {
        'order_products': order_products,
        'products': products,
        'order' : order,
        'total' : total,
    }

    payment_status = order.payment.status
    
    if payment_status == 'Completed':
        return render(request, 'order_placed.html', context)
        
    if request.method == 'POST':
        payment_type = order.payment.payment_method

        if payment_type == 'Cash on delivery':
            order.status = 'Accepted'
            order.is_ordered = True
            order.save()

            order.payment.status = 'Completed'
            order.payment.save()

            context = {
                'order_products': order_products,
                'products': products,
                'order' : order,
                'total' : total,
            }

            return render(request, 'order_placed.html', context)
        
        elif payment_type == 'paypal':
            return HttpResponseRedirect(reverse('create_payment', args=[order.order_id]))

        elif payment_type == 'Wallet':
            wallet = Wallet.objects.get(user=request.user)
            wallet.balance -= order.order_total
            wallet.save()

            order.status = 'Accepted'
            order.is_ordered = True
            order.save()

            order.payment.status = 'Completed'
            order.payment.save()

            context = {
                'order_products': order_products,
                'products': products,
                'order' : order,
                'total' : total,
            }

            return render(request, 'order_placed.html', context)
        
    context = {
        'order_products': order_products,
        'products': products,
        'order' : order,
        'total' : total,
    }

    return render(request, 'order_confirmation.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def generate_invoice_pdf(request, order_id):
    order = Order.objects.get(order_id=order_id)
    try:
        # Try to get the OrderProduct object using get()
        order_products = OrderProduct.objects.filter(order_id=order_id)

        if not order_products:
            raise Http404("Order product not found")
    except OrderProduct.DoesNotExist:
        # If no object is found, raise a specific error message
        raise Http404("Order product not found")

    products = [product.product for product in order_products]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    # Create a PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw the invoice header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Invoice")
    p.drawString(100, 780, "TechTrove")

    # Draw customer information and shipping address
    p.setFont("Helvetica", 12)
    p.drawString(100, 760, f"Customer: {order.full_name}")
    p.drawString(100, 740, f"Order Number: {order.order_number}")

    # Draw additional customer information based on your requirements
    # ...

    p.drawString(100, 720, "Shipping Address:")
    p.drawString(120, 700, order.address.address_line)
    p.drawString(120, 680, order.address.street_name)
    p.drawString(120, 660, order.address.city)
    p.drawString(120, 640, order.address.state)
    p.drawString(120, 620, order.address.country)
    p.drawString(120, 600, order.address.zip_code)

    # Draw a line separator
    p.line(100, 580, 500, 580)

    # Draw ordered products
    p.drawString(100, 560, "Ordered Products:")
    y_position = 540

    for product in products:
        p.drawString(120, y_position, f"Product: {product.product_name}")
        p.drawString(120, y_position - 20, f"Price: ₹{product.price}")
        # Add more product details based on your requirements
        # ...

        y_position -= 40

    # Draw total and other summary information
    # ...

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    return response

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def order_details(request, order_id):
    order = Order.objects.get(order_id=order_id)
    try:
        # Try to get the OrderProduct object using get()
        order_products = OrderProduct.objects.filter(order_id=order_id)

        if not order_products:
            raise Http404("Order product not found")
    except OrderProduct.DoesNotExist:
        # If no object is found, raise a specific error message
        raise Http404("Order product not found")

    products = [product.product for product in order_products]
    
    context = {
        'order_products':order_products,
        'order':order,
        'products': products,
    }

    return render(request, 'order_detail.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def cancel_order(request, order_id):
    user = request.user
    email = user.email
    try:
        order = get_object_or_404(Order, order_id=order_id)

    except Order.DoesNotExist:
        messages.info(request, 'You dont have any orders yet.')

    if request.method == "POST":
        if order.payment.payment_method == 'Cash on delivery':
            order.status = 'Cancelled'
            order.save()
            order.payment.status = 'Cancelled'
            order.payment.save()
        
        elif order.payment.payment_method == 'paypal':
            order.status = 'Cancelled'
            order.save()

            return HttpResponseRedirect(reverse('process_refund', args=[order.order_id]))

        # Send cancellation mail
        send_mail("Order cancellation: ", f"Your order:{order.order_number}- for {order.full_name} is cancelled", settings.EMAIL_HOST_USER, [email], fail_silently=False)
        messages.success(request, 'Your order succesfully cancelled!!')
    
    return redirect('user_profile')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def admin_order_details(request):
    try:
        order_product = OrderProduct.objects.all()
        orders = Order.objects.all().order_by('-created_at')
        products = []

        for product in order_product:
            products.append(product)

    except Order.DoesNotExist:
        pass
    
    context = {
        'orders':orders,
        'order_product': order_product,
        'products': products,
    }

    return render(request, 'admin_order_details.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def admin_order_detailed_view(request, order_id):
    order = Order.objects.get(order_id=order_id)
    try:
        # Try to get the OrderProduct object using get()
        order_products = OrderProduct.objects.filter(order_id=order_id)

        if not order_products:
            raise Http404("Order product not found")
    except OrderProduct.DoesNotExist:
        # If no object is found, raise a specific error message
        raise Http404("Order product not found")

    products = [product.product for product in order_products]

    if request.method == 'POST':
        order_form = OrderStatusForm(request.POST, instance=order)
        payment_form = PaymentStatusForm(request.POST, instance=order.payment)

        if order_form.is_valid():
            order_form.save()

        if payment_form.is_valid():
            payment_form.save()
    else:
        order_form = OrderStatusForm(instance=order)
        payment_form = PaymentStatusForm(instance=order.payment)

    context = {
        'order_products': order_products,
        'products': products,
        'order' : order,
        'order_form' : order_form,
        'payment_form' : payment_form,
    }

    return render(request, 'admin_order_update.html', context)


