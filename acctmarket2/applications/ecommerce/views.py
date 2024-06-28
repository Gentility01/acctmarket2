import json
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  TemplateView, UpdateView, View)

from acctmarket2.applications.ecommerce.forms import (CategoryForm, ProductForm,
                                               ProductImagesForm,
                                               ProductReviewForm, TagsForm)
from acctmarket2.applications.ecommerce.models import (CartOrder, CartOrderItems,
                                                Category, Payment, Product,
                                                ProductImages, ProductReview,
                                                Tags, WishList)
from acctmarket2.utils.payments import NowPayment
from acctmarket2.utils.views import ContentManagerRequiredMixin


class AddCategoryView(ContentManagerRequiredMixin, CreateView):
    """
    A view for adding a new category.
    """

    model = Category
    form_class = CategoryForm
    template_name = "pages/ecommerce/add_category.html"
    success_url = reverse_lazy("ecommerce:list_category")


class ListCategoryView(ContentManagerRequiredMixin, ListView):
    """
    A view for listing all categories.
    """

    model = Category
    template_name = "pages/ecommerce/category_list.html"
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.annotate(total_products=Count("product")).order_by(
            "-created_at",
        )


class EditCategoryView(ContentManagerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "pages/ecommerce/edit_category.html"
    success_url = reverse_lazy("ecommerce:list_category")


class DeleteCategoryView(ContentManagerRequiredMixin, DeleteView):
    model = Category
    template_name = "pages/ecommerce/delete_category.html"
    success_url = reverse_lazy("ecommerce:list_category")


# ---------------------- Category views ends here ----------------


class ProductImagesCreateView(ContentManagerRequiredMixin, FormView):
    template_name = "pages/ecommerce/create_product_image.html"
    form_class = ProductImagesForm
    success_url = reverse_lazy("ecommerce:list_product_images")

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        for each in self.request.FILES.getlist("image"):
            ProductImages.objects.create(image=each, product=product)
        return super().form_valid(form)


class ListProductImages(ContentManagerRequiredMixin, ListView):
    model = ProductImages
    template_name = "pages/ecommerce/list_product_imges.html"
    paginate_by = 10


class UpdateProductImages(ContentManagerRequiredMixin, UpdateView):
    model = ProductImages
    form_class = ProductImagesForm  # Use form_class instead of forms
    template_name = "pages/ecommerce/create_product_image.html"
    success_url = reverse_lazy("ecommerce:list_product_images")

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        images = self.request.FILES.getlist("image")
        for image in images:
            ProductImages.objects.create(product=product, image=image)
        return super().form_valid(form)


class DeleteProductImages(ContentManagerRequiredMixin, DeleteView):
    model = ProductImages
    template_name = "pages/ecommerce/delete_product_image.html"
    success_url = reverse_lazy("ecommerce:list_product_images")


class ListProductView(ContentManagerRequiredMixin, ListView):
    """
    A view for listing all products.
    """

    model = Product
    template_name = "pages/ecommerce/product_list.html"
    paginate_by = 10


class AddProductView(ContentManagerRequiredMixin, CreateView):
    """
    A view for adding a new product.
    """

    model = Product
    form_class = ProductForm
    template_name = "pages/ecommerce/add_product.html"
    success_url = reverse_lazy("ecommerce:list_product")


class EditProductView(ContentManagerRequiredMixin, UpdateView):
    """
    A view for editing an existing product.
    """

    model = Product
    form_class = ProductForm
    template_name = "pages/ecommerce/add_product.html"
    success_url = reverse_lazy("ecommerce:list_product")


class DeleteProductView(ContentManagerRequiredMixin, DeleteView):
    """
    A view for deleting an existing product.
    """

    model = Product
    template_name = "pages/ecommerce/delete_product.html"
    success_url = reverse_lazy("ecommerce:list_product")


class ProductDetailView(ContentManagerRequiredMixin, ListView):
    """
    A view for listing all products.
    """

    model = Product
    template_name = "ecommerce/product_detail.html"


# ---------------------------  ----------------------------------
# ---------------------- Product views ends here ----------------


class CreateProductTags(ContentManagerRequiredMixin, CreateView):
    model = Tags
    form_class = TagsForm
    template_name = "pages/ecommerce/tags_create.html"
    success_url = reverse_lazy("ecommerce:list_tags")


class EditProductTags(ContentManagerRequiredMixin, UpdateView):
    model = Tags
    form_class = TagsForm
    template_name = "pages/ecommerce/tags_create.html"
    success_url = reverse_lazy("ecommerce:list_tags")


class DeleteProductTags(ContentManagerRequiredMixin, DeleteView):
    model = Tags
    form_class = TagsForm
    template_name = "pages/ecommerce/tags_delete.html"
    success_url = reverse_lazy("ecommerce:list_tags")


class ListProductTags(ContentManagerRequiredMixin, ListView):
    model = Tags
    form_class = TagsForm
    template_name = "pages/ecommerce/tags_list.html"
    paginate_by = 10


# ---------------------------  ----------------------------------
# ---------------------- Tag views ends here ----------------


class AddReviewsView(LoginRequiredMixin, CreateView):
    model = ProductReview
    form_class = ProductReviewForm

    def form_valid(self, form):
        """
        Saves the form data and returns a JSON response containing the user"s username,
        the review text, the rating,
        and the average rating for the product.

        Parameters:
            form (ProductReviewForm): The form containing the review data.

        Returns:
            JsonResponse: A JSON response containing the following keys:
                - bool (bool): True if the form is valid, False otherwise.
                - context (dict): A dictionary containing the user"s username,
                  the review text, and the rating.
                - average_review (dict): A dictionary containing the average rating for
                the product.

        Raises:
            Product.DoesNotExist: If the product with the
            given primary key does not exist.
        """

        # Check if the user is authenticated and if the user has added a review already
        product = form.instance.product

        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(pk=self.kwargs["pk"])
        self.object = form.save()

        average_review = ProductReview.objects.filter(product=product).aggregate(
            rating=Avg("rating"),
        )

        context = {
            "user": self.request.user.name,
            "review": form.instance.review,
            "rating": form.instance.rating,
        }

        return JsonResponse(
            {
                "bool": True,
                "context": context,
                "average_review": average_review,
            },
        )

    def form_invalid(self, form):
        return JsonResponse(
            {
                "bool": False,
                "errors": form.errors,
            },
        )


# ---------------------------  ----------------------------------
# ---------------------- Add reviews ends here ----------------


class AddToCartView(View):
    def get(self, request, *args, **kwargs):
        """
        Adds a product to the cart session data.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            JsonResponse: A JSON response containing the updated cart
            data and the total number of items in the cart.

        Description:
            This function is used to add a product to the cart session data.
            It takes the request object as a parameter,
            along with any additional arguments and keyword arguments.
            The function retrieves the product details from the request GET parameters
            and creates a dictionary representation of the product.
            It then checks if there is already a cart data object in the session.
            If there is, it updates the quantity of the product
            if it already exists in the cart, otherwise
            it adds the product to the cart data. Finally,
            it returns a JSON response containing the updated
            cart data and the total number of items in the cart.
        """

        cart_product = {
            str(request.GET.get("id")): {
                "title": request.GET.get("title"),
                "quantity": request.GET.get("qty"),
                "price": request.GET.get("price"),
                "image": request.GET.get("image"),
                "pid": request.GET.get("product_id"),
            },
        }

        if "cart_data_obj" in request.session:
            cart_data = request.session["cart_data_obj"]
            product_id = str(request.GET.get("id"))
            if product_id in cart_data:
                cart_data[product_id]["quantity"] = int(
                    cart_product[product_id]["quantity"],
                )
            else:
                cart_data.update(cart_product)
            request.session["cart_data_obj"] = cart_data
        else:
            request.session["cart_data_obj"] = cart_product

        return JsonResponse(
            {
                "data": request.session["cart_data_obj"],
                "totalcartitems": len(request.session["cart_data_obj"]),
            },
        )


# ---------------------------  ----------------------------------
# ---------------------- Add to cart  ends here ----------------


class CartListView(TemplateView):
    """
    A view that displays the cart items and calculates the total amount.

    This view retrieves the cart data from the session and calculates the total amount
    based on the quantity and price of each item in the cart. It then renders the
    "pages/ecommerce/cart_list.html" template, passing the cart data, total cart items,
    and total amount as context variables.
    """

    template_name = "pages/ecommerce/cart_list.html"

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and checks if the cart is empty.
        Redirects to the home page with a warning message if the cart is empty.
        """
        if (
            "cart_data_obj" not in request.session
            or not request.session["cart_data_obj"]
        ):
            messages.warning(request, "Your cart is empty.")
            return redirect("homeapp:home")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data for the view.

        Parameters:
            **kwargs (dict): Additional keyword arguments.

        Returns:
            dict: The context data containing the following keys:
                - cart_data (dict): The cart data stored in the session.
                - totalcartitems (int): The total number of items in the cart.
                - cart_total_amount (float): The total amount of the items in the cart.
        """
        context = super().get_context_data(**kwargs)
        cart_total_amount = 0
        cart_data = self.request.session["cart_data_obj"]

        for product_id, item in cart_data.items():
            cart_total_amount += int(item["quantity"]) * float(item["price"])

        context["cart_data"] = cart_data
        context["totalcartitems"] = len(cart_data)
        context["cart_total_amount"] = cart_total_amount

        return context


# ---------------------------  ----------------------------------
# ---------------------- Cart List  ends here ----------------


class DeleteFromCartView(View):
    def get(self, request, *args, **kwargs):
        product_id = str(request.GET.get("id"))
        self.remove_item_from_cart(request, product_id)

        cart_total_amount = self.calculate_cart_total(request)

        context = render_to_string(
            "pages/async/cart_list.html",
            {
                "cart_data": request.session.get("cart_data_obj", {}),
                "totalcartitems": len(request.session.get("cart_data_obj", {})),
                "cart_total_amount": cart_total_amount,
            },
        )
        return JsonResponse(
            {
                "data": context,
                "totalcartitems": len(request.session.get("cart_data_obj", {})),
            },
        )

    def remove_item_from_cart(self, request, product_id):
        if "cart_data_obj" in request.session:
            cart_data = request.session["cart_data_obj"]
            if product_id in cart_data:
                del cart_data[product_id]
                request.session["cart_data_obj"] = cart_data

    def calculate_cart_total(self, request):
        cart_total_amount = 0
        if "cart_data_obj" in request.session:
            for item in request.session["cart_data_obj"].values():
                cart_total_amount += int(item["quantity"]) * float(item["price"])
        return cart_total_amount


# ---------------------------  ----------------------------------
# ---------------------- Delete from cart  ends here ----------------


class UpdateCartView(View):
    def get(self, request, *args, **kwargs):
        product_id = str(request.GET.get("id"))
        new_quantity = int(request.GET.get("quantity", 1))
        self.update_item_in_cart(request, product_id, new_quantity)

        cart_total_amount = self.calculate_cart_total(request)

        context = render_to_string(
            "pages/async/cart_list.html",
            {
                "cart_data": request.session.get("cart_data_obj", {}),
                "totalcartitems": len(request.session.get("cart_data_obj", {})),
                "cart_total_amount": cart_total_amount,
            },
        )
        return JsonResponse(
            {
                "data": context,
                "totalcartitems": len(request.session.get("cart_data_obj", {})),
            },
        )

    def update_item_in_cart(self, request, product_id, new_quantity):
        if "cart_data_obj" in request.session:
            cart_data = request.session["cart_data_obj"]
            if product_id in cart_data:
                cart_data[product_id]["quantity"] = new_quantity
                request.session["cart_data_obj"] = cart_data

    def calculate_cart_total(self, request):
        cart_total_amount = 0
        if "cart_data_obj" in request.session:
            for item in request.session["cart_data_obj"].values():
                cart_total_amount += int(item["quantity"]) * float(item["price"])
        return cart_total_amount


# ---------------------------  ----------------------------------
# ---------------------- Update Cart  ends here ----------------


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_data = self.request.session.get(
            "cart_data_obj",
            {},
        )  # Fetch cart data from session

        # Calculate total cart amount
        cart_total_amount = sum(
            Decimal(item["price"]) * int(item["quantity"])
            for item in cart_data.values()
        )

        # Create an order in the database
        order = CartOrder.objects.create(
            user=self.request.user,
            price=cart_total_amount,
            paid_status=False,
        )

        # Create order items in the database
        order_items = [
            CartOrderItems(
                order=order,
                product=get_object_or_404(Product, id=product_id),
                invoice_no=f"INVOICE_NO_{order.id}",
                quantity=int(item["quantity"]),
                price=Decimal(item["price"]),
                total=Decimal(item["price"]) * int(item["quantity"]),
            )
            for product_id, item in cart_data.items()
        ]

        CartOrderItems.objects.bulk_create(order_items)

        user = self.request.user
        # Update context with necessary data
        context.update(
            {
                "user_name": user.name,
                "user_email": user.email,
                "user_country": user.country,
                "user_phone": user.phone_no,
                "cart_data": cart_data,
                "totalcartitems": len(cart_data),
                "cart_total_amount": cart_total_amount,
                "order_price": order.price,
                "order_id": order.id,
            },
        )

        return context


class ProceedPayment(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_data = self.request.session.get(
            "cart_data_obj",
            {},
        )  # Fetch cart data from session

        # Calculate total cart amount
        cart_total_amount = sum(
            Decimal(item["price"]) * int(item["quantity"])
            for item in cart_data.values()
        )

        # Create an order in the database
        order = CartOrder.objects.create(
            user=self.request.user,
            price=cart_total_amount,
            paid_status=False,
        )

        # Create order items in the database
        order_items = [
            CartOrderItems(
                order=order,
                product=get_object_or_404(Product, id=product_id),
                invoice_no=f"INVOICE_NO_{order.id}",
                quantity=int(item["quantity"]),
                price=Decimal(item["price"]),
                total=Decimal(item["price"]) * int(item["quantity"]),
            )
            for product_id, item in cart_data.items()
        ]

        CartOrderItems.objects.bulk_create(order_items)

        user = self.request.user
        # Update context with necessary data
        context.update(
            {
                "user_name": user.name,
                "user_email": user.email,
                "user_country": user.country,
                "user_phone": user.phone_no,
                "cart_data": cart_data,
                "totalcartitems": len(cart_data),
                "cart_total_amount": cart_total_amount,
                "order_price": order.price,
                "order_id": order.id,
            },
        )

        return context

    # Overriding the get method to redirect to initiate payment
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return redirect("ecommerce:initiate_payment", order_id=context["order_id"])


class InitiatePaymentView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/initiate_payment.html"

    # Overriding the get method to initialize payment
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(CartOrder, id=order_id, user=request.user)

        # Get or create a payment record
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": request.user,
                "amount": order.price,
            },
        )

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": request.user.email,
            "amount": payment.amount_value(),  # Amount in kobo
            "reference": payment.reference,
            "callback_url": request.build_absolute_uri(
                reverse("ecommerce:verify_payment", args=[payment.reference]),
            ),
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=data,
        )
        response_data = response.json()

        if response_data.get("status") is True:  # Ensure the status is True
            authorization_url = response_data["data"]["authorization_url"]
            # Redirect to the authorization URL or handle it accordingly
            return redirect(authorization_url)
        else:
            print(f"Paystack initialization error: {response_data}")
            messages.error(
                request,
                f"""
                Error initializing payment:
                {response_data.get("message", "Unknown error")}
                """,
            )
            return redirect("ecommerce:checkout")


class VerifyPaymentView(LoginRequiredMixin, View):
    def get(self, request, reference, *args, **kwargs):
        payment = get_object_or_404(Payment, reference=reference)
        verified = payment.verify_payment()
        if verified:
            # Send an email with the link to the purchased products page
            purchased_product_url = request.build_absolute_uri(
                reverse("ecommerce:purchased_products"),
            )
            send_mail(
                "Your Purchase is Complete",
                f"""
                    Thank you for your purchase.
                    You can access your purchased products here: {purchased_product_url}
                """,
                # Update this if you set DEFAULT_FROM_EMAIL in settings
                f"from {settings.DEFAULT_FROM_EMAIL}",
                [request.user.email],
                fail_silently=False,
            )
            messages.success(
                request,
                """
                    Verification successful.
                    check your mail to access the products you purchase
                """,
            )
            return redirect("ecommerce:payment_complete")
        else:
            messages.error(request, "Verification failed")
            return redirect("ecommerce:payment_failed")


class PaymentCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/payment_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_total_amount = Decimal("0.00")

        cart_data_obj = self.request.session.get("cart_data_obj", {})

        if cart_data_obj:
            for item in cart_data_obj.values():
                cart_total_amount += int(item["quantity"]) * Decimal(item["price"])

        context["cart_data"] = cart_data_obj
        context["totalcartitems"] = len(cart_data_obj)
        context["cart_total_amount"] = cart_total_amount

        # Clear the session cart data
        if "cart_data_obj" in self.request.session:
            del self.request.session["cart_data_obj"]

        return context


class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/payment_failed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_data_obj = self.request.session.get("cart_data_obj", {})
        context["cart_data"] = cart_data_obj
        context["totalcartitems"] = len(cart_data_obj)
        return context


class PurchasedProductsView(LoginRequiredMixin, ListView):
    template_name = "pages/ecommerce/purchased_products.html"
    context_object_name = "purchased_products"

    def get_queryset(self):
        return Product.objects.filter(
            id__in=CartOrderItems.objects.filter(
                order__user=self.request.user,
                order__paid_status=True,
            ).values_list("product_id", flat=True),
        )

    def dispatch(self, request, *args, **kwargs):
        # Check if the user has any completed orders
        if not CartOrder.objects.filter(user=request.user, paid_status=True).exists():
            messages.warning(request, "You need to make a purchase first.")
            return redirect("ecommerce:checkout")
        return super().dispatch(request, *args, **kwargs)


class WishlistListView(LoginRequiredMixin, ListView):
    model = WishList
    template_name = "pages/ecommerce/wish_list.html"
    context_object_name = "wishlists"


class AddToWishlistView(View):

    def get(self, request, *args, **kwargs):

        product_id = request.GET.get("id")
        product = get_object_or_404(Product, id=product_id)

        context = {}

        wishlist_count = WishList.objects.filter(
            product=product,
            user=request.user,
        ).count()
        print(wishlist_count)

        if wishlist_count > 0:
            context = {
                "bool": True,
            }
        else:
            WishList.objects.create(
                product=product,
                user=request.user,
            )
            context = {
                "bool": True,
            }

        return JsonResponse(context)



class NowPaymentView(View):

    def get_supported_currencies(self):
        headers = {
            'x-api-key': settings.NOWPAYMENTS_API_KEY
        }
        response = requests.get('https://api.nowpayments.io/v1/currencies', headers=headers)
        if response.status_code == 200:
            return response.json()['currencies']
        return []

    def get(self, request, order_id):
        order = get_object_or_404(CartOrder, id=order_id, user=request.user)
        supported_currencies = self.get_supported_currencies()
        return render(request, 'pages/ecommerce/create_nowpayment.html', {
            'supported_currencies': supported_currencies,
            'order': order
        })

    def post(self, request, order_id):
        order = get_object_or_404(CartOrder, id=order_id, user=request.user)
        pay_currency = request.POST.get('pay_currency')

        # Prepare the request payload
        payload = {
            'price_amount': str(order.price),
            'price_currency': 'USD',  # Assuming the order price is in USD
            'pay_currency': pay_currency,
            'ipn_callback_url': 'https://yourwebsite.com/ipn/',  # IPN URL
            'order_id': str(order.id),
            'order_description': f'Order #{order.id} for user {order.user.id}'
        }

        # Send the request to NOWPayments
        headers = {
            'x-api-key': settings.NOWPAYMENTS_API_KEY
        }
        response = requests.post('https://api.nowpayments.io/v1/invoice', json=payload, headers=headers)

        # Process the response
        if response.status_code == 200:
            response_data = response.json()
            return redirect(response_data['invoice_url'])
        else:
            return JsonResponse(response.json(), status=response.status_code)


@csrf_exempt
def ipn(request):
    if request.method == 'POST':
        data = request.POST
        # Process the IPN data here (e.g., update order status)
        print(data)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)