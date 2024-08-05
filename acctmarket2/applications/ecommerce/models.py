import logging
import secrets
import uuid
from decimal import Decimal

import auto_prefetch
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, SET_NULL, BooleanField, CharField,
                              DateTimeField, DecimalField, FileField,
                              IntegerField, JSONField, SlugField, TextField)
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from acctmarket2.utils.choices import ProductStatus, Rating, Status
from acctmarket2.utils.media import MediaHelper
from acctmarket2.utils.models import (ImageTitleTimeBaseModels, TimeBasedModel,
                                      TitleandUIDTimeBasedModel)
from acctmarket2.utils.payments import NowPayment, PayStack

# Create your models here.


logger = logging.getLogger(__name__)


class Permissions:
    CAN_CRUD_PRODUCT = Permission.objects.filter(
        codename__in=["add_product", "change_product", "delete_product"],
    )
    CAN_CRUD_CATEGORY = Permission.objects.filter(
        codename__in=["add_category", "change_category", "delete_category"],
    )


class Category(ImageTitleTimeBaseModels):
    slug = SlugField(default="", blank=True)
    sub_category = auto_prefetch.ForeignKey(
        "self",
        on_delete=CASCADE,
        blank=True,
        null=True,
        related_name="subcategories",
    )

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        """
        Saves the instance with a slug generated
        from the title if no slug is provided.

        Parameters:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(TitleandUIDTimeBasedModel, ImageTitleTimeBaseModels):
    user = auto_prefetch.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        on_delete=SET_NULL,
        null=True,
    )
    category = auto_prefetch.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=SET_NULL,
        null=True,
    )
    description = RichTextUploadingField("Description", default="", null=True)
    price = DecimalField(
        max_digits=100,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    oldprice = DecimalField(
        max_digits=100,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    quantity_in_stock = IntegerField(blank=True, null=True)
    specification = RichTextUploadingField(
        "specification", default="", null=True
    )
    product_status = CharField(
        choices=Status.choices,
        default=Status.IN_REVIEW,
        max_length=10,
    )
    tags = TaggableManager(
        blank=True, help_text="A comma-separated list of tags."
    )
    in_stock = BooleanField(default=True)
    featured = BooleanField(default=False)
    digital = BooleanField(default=True)
    best_seller = BooleanField(default=False)
    special_offer = BooleanField(default=False)
    just_arrived = BooleanField(default=True)
    deal_of_the_week = BooleanField(default=False)
    deal_start_date = DateTimeField(null=True, blank=True)
    deal_end_date = DateTimeField(null=True, blank=True)
    resource = FileField(
        upload_to=MediaHelper.get_file_upload_path,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Products"
        ordering = ["-created_at", "-updated_at"]
        permissions = [
            ("can_crud_product", "Can create, update, and delete product"),
        ]

    def get_percentage(self, decimal_places=2):
        if self.oldprice > 0:
            percentage = ((self.oldprice - self.price) / self.oldprice) * 100
            return round(percentage, decimal_places)

        return 0

    def get_discount_price(self):
        if self.oldprice > 0:
            return self.oldprice - self.price

    def get_deal_price(self):
        if (
            self.deal_of_the_week
            and self.deal_start_date <= timezone.now() <= self.deal_end_date
        ):
            return self.price * (1 - self.discount_percentage / 100)
        return self.price

    def __str__(self):
        if not self.title:
            logger.error(f"Product ID {self.id} has no title")
            return f"Product ID {self.id}"
        return self.title


class ProductKey(TimeBasedModel):
    product = auto_prefetch.ForeignKey(
        "ecommerce.Product",
        verbose_name=_("Product Key"),
        on_delete=SET_NULL,
        null=True,
    )
    key = CharField(max_length=255)
    password = CharField(max_length=255)
    is_used = BooleanField(default=False)

    def __str__(self) -> str:
        return (
            f"key for {self.product.title} - key {self.key} - password{self.password}"  # noqa
        )


class ProductImages(ImageTitleTimeBaseModels):
    product = auto_prefetch.ForeignKey(
        Product,
        verbose_name=_("Product image"),
        on_delete=SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Product images"


class CartOrder(TimeBasedModel):
    user = auto_prefetch.ForeignKey(
        "users.User",
        verbose_name=_("User Order"),
        on_delete=CASCADE,
        null=True,
        related_name="cart_orders",
    )
    price = DecimalField(
        max_digits=100,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    paid_status = BooleanField(default=False)
    product_status = CharField(
        choices=ProductStatus.choices,
        default=ProductStatus.PROCESSING,
        max_length=30,
    )
    payment_method = CharField(max_length=20, blank=True)

    class Meta:
        verbose_name_plural = "Cart Orders"

    def __str__(self):
        return f"{self.user}'s cart order"


class CartOrderItems(TimeBasedModel):
    transaction_id = CharField(
        default=uuid.uuid4, editable=False, unique=True, blank=True
    )
    order = auto_prefetch.ForeignKey(
        CartOrder,
        verbose_name=_("Order"),
        on_delete=CASCADE,
        null=True,
        related_name="order_items",
    )
    product = auto_prefetch.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=SET_NULL,
        null=True,
    )
    unique_key = CharField(max_length=255, blank=True, null=True)
    quantity = IntegerField(default=1, validators=[MinValueValidator(1)])
    price = DecimalField(
        max_digits=100,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total = DecimalField(
        max_digits=100,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    invoice_no = CharField(max_length=20, default="", blank=True)
    keys_and_passwords = JSONField(default=list, blank=True)

    class Meta:
        verbose_name_plural = "Cart Order Items"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """
        Saves the object after checking and generating
        a transaction ID if not already set.
        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)

    def unique_keys_list(self):
        return [entry["key"] for entry in self.keys_and_passwords]

    def __str__(self):
        return f"{self.product} - {self.quantity} item(s)"


class Payment(TimeBasedModel):
    user = auto_prefetch.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="payments",
        default="",
        blank=True,
    )
    order = auto_prefetch.OneToOneField(
        "ecommerce.CartOrder",
        on_delete=CASCADE,
        related_name="payment",
        default="",
        blank=True,
    )
    amount = DecimalField(
        max_digits=100, decimal_places=2, default="", blank=True
    )
    reference = CharField(
        max_length=100, unique=True, default="", blank=True
    )
    status = CharField(
        max_length=20, default="pending", blank=True
    )
    verified = BooleanField(default=False)

    def __str__(self) -> str:
        return f"Payment for {self.order}"

    def save(self, *args, **kwargs) -> None:
        if not self.reference:
            while True:
                reference = secrets.token_urlsafe(20)
                if not Payment.objects.filter(reference=reference).exists():
                    self.reference = reference
                    break
        super().save(*args, **kwargs)

    def amount_value(self) -> int:
        return int(self.amount * 100)

    def verify_paystack_payment(self) -> bool:
        # Paystack payment verification
        paystack = PayStack()
        status, result = paystack.verify_payment(self.reference)
        if status:
            paystack_amount = Decimal(result["amount"]) / 100  # Amount in kobo to NGN                # noqa
            self.amount = paystack_amount
            if paystack_amount == self.amount:
                self.status = "verified"
                self.save()
                self.order.paid_status = True
                self.order.save()
                return True
        self.status = "failed"
        self.save()
        return False

    def verify_payment_nowpayments(self):
        nowpayment = NowPayment()
        result = nowpayment.verify_payment(self.reference)
        logging.info(f"NowPayments verification result: {result}")
        if not result:
            logging.error("No response from NowPayments API")
            self.status = "failed"
            self.save()
            return False
        if result and result.get("payment_status") == "confirmed":
            nowpayments_amount = Decimal(result["pay_amount"])
            if nowpayments_amount == self.amount:
                self.status = "verified"
                self.verified = True
                self.amount = nowpayments_amount
                self.save()
                self.order.paid_status = True
                self.order.save()
                return True
        self.status = "failed2"
        self.save()
        return False

    @staticmethod
    def generate_unique_reference():
        while True:
            reference = str(uuid.uuid4())
            if not Payment.objects.filter(reference=reference).exists():
                return reference


class ProductReview(TimeBasedModel):
    user = auto_prefetch.ForeignKey(
        "users.User",
        verbose_name=_("User Review"),
        on_delete=SET_NULL,
        null=True,
    )
    product = auto_prefetch.ForeignKey(
        Product,
        verbose_name=_("Product Review"),
        on_delete=SET_NULL,
        null=True,
    )
    review = TextField()
    rating = IntegerField(choices=Rating.choices, default=Rating.THREE_STARS)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def get_rating(self):
        return self.rating


class WishList(TimeBasedModel):
    user = auto_prefetch.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        on_delete=SET_NULL,
        null=True,
    )
    product = auto_prefetch.ForeignKey(
        Product,
        verbose_name=_("Product Wishlist"),
        on_delete=SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Wishlists"

    def get_rating(self):
        return f"products wishlist : {self.rating}"   # noqa


class Address(TimeBasedModel):
    user = auto_prefetch.ForeignKey(
        "users.User",
        verbose_name=_("User Address"),
        on_delete=SET_NULL,
        null=True,
    )
    address = CharField(max_length=100, default="", blank=True)
    status = BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

    def get_rating(self):
        return f"products address : {self.address}"  # noqa
