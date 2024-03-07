from product_category.models import Category


def categories(request):
    items = Category.objects.all()
    return {'items': items}