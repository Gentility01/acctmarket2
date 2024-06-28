from django.db.models import Max, Min
from django.utils import timezone

from acctmarket2.applications.blog.models import Banner, BlogCategory, Post
from acctmarket2.applications.ecommerce.models import Category, Product, WishList


def product_list(request):
    """
    Context processor to provide a list of products to templates.

    :param request: HTTP request object
    :return: Dictionary containing the product list
    """
    products = Product.objects.all().order_by("-created_at", "-updated_at", "-id")
    blog_categories = BlogCategory.objects.all().order_by("-created_at")
    blog_posts = Post.objects.all().order_by("-created_at")
    in_stock = products.filter(in_stock=True)

    best_seller = products.filter(best_seller=True)
    special_offer = products.filter(special_offer=True)
    featured = products.filter(featured=True)
    just_arrived = products.filter(just_arrived=True)
    just_arrived2 = products.filter(just_arrived=True).order_by("-id")
    categories = Category.objects.all().order_by("-id")
    deal_product  = products.filter(deal_of_the_week=True, deal_start_date__lte=timezone.now(), deal_end_date__gte=timezone.now()).first()

    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    banners = Banner.objects.all().order_by("-created_at")

    try:
        wishlist = WishList.objects.filter(user=request.user)
    except:
        # messages.warning(request, "Please Login to access wishlist.")
        wishlist = 0

    return {
        "in_stock": in_stock,
        "best_seller": best_seller,
        "special_offer": special_offer,
        "featured": featured,
        "top_categories": categories,
        "just_arrived": just_arrived,
        "just_arrived2": just_arrived2,
        "all_products": products,
        "min_max_price": min_max_price,
        "blog_categories": blog_categories,
        "blog_posts": blog_posts,
        "banners": banners,
        "wishlist": wishlist,
        "deal_product":deal_product,
    }


def products_by_category(request):
    category_id = request.GET.get(
        "category_id",
    )  # Assuming the category_id is passed in the query parameters
    products = []
    if category_id:
        products = Product.objects.filter(category__id=category_id)
    return {"filtered_products": products}
