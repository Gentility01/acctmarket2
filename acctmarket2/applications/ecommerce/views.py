import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  TemplateView, UpdateView, View)

from acctmarket2.applications.ecommerce.forms import (CategoryForm,
                                                      ProductForm,
                                                      ProductImagesForm,
                                                      ProductKeyFormSet,
                                                      ProductReviewForm)
from acctmarket2.applications.ecommerce.models import (CartOrder,
                                                       CartOrderItems,
                                                       Category, Payment,
                                                       Product, ProductImages,
                                                       ProductKey,
                                                       ProductReview, WishList)
from acctmarket2.utils.views import ContentManagerRequiredMixin

logger = logging.getLogger(__name__)


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
        return Category.objects.annotate(
            total_products=Count("product")).order_by(
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


class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "pages/ecommerce/add_product.html"
    success_url = reverse_lazy("ecommerce:list_product")

    def form_valid(self, form):
        response = super().form_valid(form)
        key_formset = ProductKeyFormSet(
            self.request.POST, instance=self.object
        )
        if key_formset.is_valid():
            key_formset.save()
        else:
            return self.form_invalid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["key_formset"] = ProductKeyFormSet(self.request.POST)
        else:
            context["key_formset"] = ProductKeyFormSet()
        return context


class EditProductView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "pages/ecommerce/add_product.html"
    success_url = reverse_lazy("ecommerce:list_product")

    def form_valid(self, form):
        response = super().form_valid(form)
        key_formset = ProductKeyFormSet(
            self.request.POST, instance=self.object
        )
        if key_formset.is_valid():
            key_formset.save()
        else:
            return self.form_invalid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["key_formset"] = ProductKeyFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["key_formset"] = ProductKeyFormSet(
                instance=self.object)
        return context


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


class AddReviewsView(LoginRequiredMixin, CreateView):
    model = ProductReview
    form_class = ProductReviewForm

    def form_valid(self, form):
        """
        Saves the form data and returns a JSON response containing
        the user"s username,
        the review text, the rating,
        and the average rating for the product.

        Parameters:
            form (ProductReviewForm): The form containing the review data.

        Returns:
            JsonResponse: A JSON response containing the following keys:
                - bool (bool): True if the form is valid, False otherwise.
                - context (dict): A dictionary containing the user"s username,
                  the review text, and the rating.
                - average_review (dict): A dictionary containing the
                average rating for
                the product.

        Raises:
            Product.DoesNotExist: If the product with the
            given primary key does not exist.
        """

        # Check if the user is authenticated and if the user has
        # added a review already
        product = form.instance.product

        form.instance.user = self.request.user
        form.instance.product = Product.objects.get(pk=self.kwargs["pk"])
        self.object = form.save()

        average_review = ProductReview.objects.filter(product=product).aggregate(   # noqa
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
            The function retrieves the product details from the request
            GET parameters
            and creates a dictionary representation of the product.
            It then checks if there is already a cart data object
            in the session.
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

    This view retrieves the cart data from the session and calculates
    the total amount
    based on the quantity and price of each item in the cart. It then renders
      the
    "pages/ecommerce/cart_list.html" template, passing the cart data, total
    cart items,
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
                - cart_total_amount (float): The total amount of the items
                in the cart.
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
                "totalcartitems": len(request.session.get(
                    "cart_data_obj", {})),
                "cart_total_amount": cart_total_amount,
            },
        )
        return JsonResponse(
            {
                "data": context,
                "totalcartitems": len(request.session.get(
                    "cart_data_obj", {})),
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
                cart_total_amount += int(
                    item["quantity"]) * float(item["price"])
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
                "totalcartitems": len(request.session.get(
                    "cart_data_obj", {})),
                "cart_total_amount": cart_total_amount,
            },
        )
        return JsonResponse(
            {
                "data": context,
                "totalcartitems": len(request.session.get(
                    "cart_data_obj", {})),
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
                cart_total_amount += int(
                    item["quantity"]) * float(item["price"])
        return cart_total_amount


# ---------------------------  ----------------------------------
# ---------------------- Update Cart  ends here ----------------


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_data = self.request.session.get("cart_data_obj", {})

        cart_total_amount = sum(
            Decimal(item["price"]) * int(item["quantity"])
            for item in cart_data.values()
        )

        order = CartOrder.objects.create(
            user=self.request.user,
            price=cart_total_amount,
            paid_status=False,
        )

        order_items = []

        for product_id, item in cart_data.items():
            product = get_object_or_404(Product, id=product_id)
            quantity = int(item["quantity"])

            for _ in range(quantity):
                order_item = CartOrderItems(
                    order=order,
                    product=product,
                    invoice_no=f"INVOICE_NO_{order.id}",
                    quantity=1,
                    price=Decimal(item["price"]),
                    total=Decimal(item["price"]),
                )
                order_items.append(order_item)

        CartOrderItems.objects.bulk_create(order_items)

        user = self.request.user
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
        return redirect("ecommerce:initiate_payment",
                        order_id=context["order_id"])


class InitiatePaymentView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/initiate_payment.html"

    # Overriding the get method to initialize payment
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(CartOrder, id=order_id, user=request.user)

        # Set the payment method to Paystack
        order.payment_method = "paystack"
        order.save()

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
            messages.error(
                request,
                f"""
                Error initializing payment:
                {response_data.get("message", "Unknown error")}                   # noqa
                """,
            )
            return redirect("ecommerce:checkout")    # noqa


class VerifyPaymentView(View):
    def get(self, request, reference, *args, **kwargs):
        """
        Handles the verification of a payment based on the payment method,
        assigns unique keys to the order,
        sends a confirmation email to the user, and redirects to the
        appropriate page based on the verification result.

        Parameters:
            request: The HTTP request object.
            reference: The reference for the payment to be verified.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A redirection to different pages based on the verification status
            of the payment.
        """
        payment = get_object_or_404(Payment, reference=reference)

        # Determine the payment method from the order"s payment_method field
        #  and verify payment
        if payment.order.payment_method == "paystack":
            verified = payment.verify_paystack_payment()
        elif payment.order.payment_method == "nowpayments":
            verified = payment.verify_payment_nowpayments()
        else:
            messages.error(request, "Unknown payment method")
            return redirect("ecommerce:payment_failed")

        if verified:  # If payment is verified
            try:
                # Use a transaction to ensure atomicity
                with transaction.atomic():
                    self.assign_unique_keys_to_order(
                        payment.order.id
                    )  # Assign unique keys to the order

                # Build the URL for the purchased products page
                purchased_product_url = request.build_absolute_uri(
                    reverse("ecommerce:purchased_products"),
                )
                # Send an email to the user confirming the purchase
                send_mail(
                    "Your Purchase is Complete",
                    f"Thank you for your purchase.\nYou can access your purchased products here: {purchased_product_url}",   # noqa
                    f"from {settings.DEFAULT_FROM_EMAIL}",
                    [request.user.email],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    "Verification successful. Check your mail to access the products you purchased.",  # noqa
                )  # Show success message
                return redirect(
                    "ecommerce:payment_complete"
                )  # Redirect to payment complete page
            except ValidationError as e:  # Catch validation errors
                messages.error(
                    request, f"Verification succeeded but an issue occurred: {e!s}"   # noqa
                )  # Show error message
                return redirect("ecommerce:support")
        else:
            messages.error(
                request, "Verification failed"
            )  # Show error message if verification failed
            return redirect(
                "ecommerce:payment_failed"
            )  # Redirect to payment failed page

    def assign_unique_keys_to_order(self, order_id):
        order = get_object_or_404(CartOrder, id=order_id)

        for order_item in order.order_items.all():
            product = order_item.product
            quantity = order_item.quantity

            available_keys = ProductKey.objects.select_for_update().filter(
                product=product, is_used=False
            )[:quantity]

            if len(available_keys) < quantity:
                self.handle_insufficient_keys(order_item, available_keys)
                continue

            keys_and_passwords = []

            for i in range(quantity):
                product_key = available_keys[i]
                product_key.is_used = True
                product_key.save()

                keys_and_passwords.append(
                    {"key": product_key.key, "password": product_key.password}
                )

            order_item.keys_and_passwords = keys_and_passwords
            order_item.save()

            product.quantity_in_stock -= quantity
            if product.quantity_in_stock < 1:
                product.visible = False
            product.save()

    def handle_insufficient_keys(self, order_item, available_keys):
        keys_and_passwords = []

        for key in available_keys:
            key.is_used = True
            key.save()

            keys_and_passwords.append(
                {"key": key.key, "password": key.password})

        order_item.keys_and_passwords = keys_and_passwords
        order_item.save()

        product = order_item.product
        user = order_item.order.user
        notify_user_insufficient_keys(user, product)


def notify_user_insufficient_keys(user, product):
    # Send notification to user about the insufficient keys for the product
    send_mail(
        "Insufficient Product Keys",
        f"Dear {user.username},\n\nWe regret to inform you that there are insufficient keys available for the product '{product.title}'. Our team is working on resolving this issue.\n\nThank you for your understanding.",  # noqa
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


class PaymentCompleteView(LoginRequiredMixin, TemplateView):
    template_name = "pages/ecommerce/payment_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_total_amount = Decimal("0.00")

        cart_data_obj = self.request.session.get("cart_data_obj", {})

        if cart_data_obj:
            for item in cart_data_obj.values():
                cart_total_amount += int(item["quantity"]) * Decimal(item["price"])  # noqa

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
    context_object_name = "order_items"

    def get_queryset(self):
        return CartOrderItems.objects.filter(
            order__user=self.request.user,
            order__paid_status=True,
        ).select_related("product", "order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_items = self.get_queryset()

        for item in order_items:
            if not item.transaction_id:
                item.transaction_id = item.generate_transaction_id()
                item.save()

        context["order_items"] = order_items
        return context

    def dispatch(self, request, *args, **kwargs):
        if not CartOrder.objects.filter(
            user=request.user, paid_status=True).exists():                        # noqa
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
            "x-api-key": settings.NOWPAYMENTS_API_KEY,
        }
        response = requests.get(
            "https://api.nowpayments.io/v1/currencies", headers=headers
        )
        if response.status_code == 200:
            return response.json()["currencies"]
        return []

    def get(self, request, order_id):
        order = get_object_or_404(CartOrder, id=order_id, user=request.user)
        supported_currencies = self.get_supported_currencies()
        return render(
            request,
            "pages/ecommerce/create_nowpayment.html",
            {
                "supported_currencies": supported_currencies,
                "order": order,
            },
        )

    def post(self, request, order_id):
        order = get_object_or_404(CartOrder, id=order_id, user=request.user)
        pay_currency = request.POST.get("pay_currency")

        # Set the payment method to nowpayments
        order.payment_method = "nowpayments"
        order.save()

        # Prepare the request payload
        payload = {
            "price_amount": str(order.price),
            "price_currency": "USD",  # Assuming the order price is in USD
            "pay_currency": pay_currency,
            "ipn_callback_url": "https://yourwebsite.com/ipn/",  # IPN URL
            "order_id": str(order.id),
            "order_description": f"Order #{order.id} for user {order.user.id}",
        }

        # Send the request to NOWPayments
        headers = {
            "x-api-key": settings.NOWPAYMENTS_API_KEY,
        }
        response = requests.post(
            "https://api.nowpayments.io/v1/invoice", json=payload, headers=headers   # noqa
        )

        # Process the response
        if response.status_code == 200:
            response_data = response.json()
            return redirect(response_data["invoice_url"])
        else:
            return JsonResponse(response.json(), status=response.status_code)


# IPN (Instant Payment Notification) endpoint for NowPayments
@method_decorator(csrf_exempt, name="dispatch")
class IPNView(View):
    def post(self, request):
        data = request.POST
        payment_reference = data.get("order_id")
        payment = get_object_or_404(Payment, reference=payment_reference)
        if payment.verify_payment_nowpayments():
            # Redirect to the VerifyPaymentView
            verify_url = reverse(
                "ecommerce:verify_payment", args=[payment_reference])
            return redirect(verify_url)
        return JsonResponse({"status": "failed"}, status=400)