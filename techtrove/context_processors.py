from product_category.models import Category
from products.models import Product
from offers.models import CategoryOffer, ProductOffer
from django.utils import timezone
from cart.models import Cart, CartItem
from wishlist.models import Wishlist


def categories(request):
    items = Category.objects.all()
    products = Product.objects.filter(is_deleted=False, is_available=True)

    cart = None
    cart_items = []
    cart_total = 0
    cart_count = 0
    wishlist_items = []
    wishlist_count = 0

    try:
        cart = Cart.objects.get(user=request.user.id)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_count = cart_items.count()
        cart_total = cart.cart_total

        wishlist_items = Wishlist.objects.filter(user=request.user.id)
        wishlist_count = wishlist_items.count()
    except Cart.DoesNotExist:
        cart = None
        cart_total = 0
    except CartItem.DoesNotExist:
        cart_items = []
    except Wishlist.DoesNotExist:
        wishlist_items = []

    products_category_offers = []
    producs_product_offers = []
    for product in products:
        product_offers = ProductOffer.objects.filter(
            product=product,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
        )

        category_offers = CategoryOffer.objects.filter(
            category=product.category,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
        )

        for product_offer in product_offers:
            producs_product_offers.append(product_offer.products_with_offer(product))
            
        for category_offer in category_offers:
            products_category_offers.append(category_offer.products_with_offer(product))

    context = {
        'items' : items,
        'producs_product_offers' : producs_product_offers,
        'products_category_offers' : products_category_offers,
        'cart_items' : cart_items,
        'cart_total' : cart_total,
        'wishlist_items' : wishlist_items,
        'wishlist_count' : wishlist_count,
        'cart_count' : cart_count,

    }

    return context