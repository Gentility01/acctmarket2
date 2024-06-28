from ckeditor.widgets import CKEditorWidget
from django.forms import (CharField, CheckboxInput, ChoiceField, FileInput,
                          ModelForm, NumberInput, Select, Textarea, TextInput)
from multiupload.fields import MultiFileField
from taggit.forms import TagField

from acctmarket2.applications.ecommerce.models import (Category, Product,
                                                ProductImages, ProductReview,
                                                Tags)
from acctmarket2.utils.choices import Rating


class ProductForm(ModelForm):
    description = CharField(
        label="Description",
        widget=CKEditorWidget(
            attrs={"class": "form-control", "placeholder": "Enter product description"},
        ),
    )
    tags = TagField(required=False)

    class Meta:
        model = Product
        fields = [
            "title",
            "image",
            "description",
            "price",
            "oldprice",
            "spacification",
            "tags",
            "product_status",
            "category",
            "in_stock",
            "featured",
            "digital",
            "best_seller",
            "special_offer",
            "just_arrived",
            "resource",
            "unique_keys",
        ]
        widgets = {
            "title": TextInput(
                attrs={"class": "form-control", "placeholder": "Enter product name"},
            ),
            "image": FileInput(
                attrs={"class": "form-control", "id": "myFile", "name": "filename"},
            ),
            "description": CKEditorWidget(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product description",
                },
            ),
            "price": NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter product price"},
            ),
            "oldprice": NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product old price",
                },
            ),
            "spacification": CKEditorWidget(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product specification",
                },
            ),
            "tags": TextInput(attrs={"class": "form-control"}),
            "product_status": Select(
                attrs={"class": "form-control", "placeholder": "Enter product status"},
            ),
            "category": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product category",
                },
            ),
            "in_stock": CheckboxInput(attrs={"class": "form-check-input"}),
            "featured": CheckboxInput(attrs={"class": "form-check-input"}),
            "digital": CheckboxInput(attrs={"class": "form-check-input"}),
            "best_seller": CheckboxInput(attrs={"class": "form-check-input"}),
            "special_offer": CheckboxInput(attrs={"class": "form-check-input"}),
            "just_arrived": CheckboxInput(attrs={"class": "form-check-input"}),
            "resource": FileInput(
                attrs={
                    "class": "form-control",
                    "id": "resourceFile",
                    "name": "resource",
                },
            ),
            "unique_keys": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter unique keys as JSON",
                    "rows": 3,
                },
            ),
        }


class ProductImagesForm(ModelForm):
    """Form to get all product images"""

    image = MultiFileField(min_num=1, max_num=10, max_file_size=1024 * 1024 * 5)

    class Meta:
        model = ProductImages
        fields = ["image", "product"]

        widgets = {
            "product": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter product",
                },
            ),
        }


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ["title", "image", "sub_category"]
        widgets = {
            "title": TextInput(
                attrs={"class": "flex-grow", "placeholder": "Enter category name"},
            ),
            "image": FileInput(attrs={"class": "form-control", "name": "filename"}),
            "sub_category": Select(attrs={"class": "form-control"}),
        }


class TagsForm(ModelForm):
    class Meta:
        model = Tags
        fields = ["title"]
        widgets = {
            "title": TextInput(
                attrs={"class": "flex-grow", "placeholder": "Enter tag name"},
            ),
        }


class ProductReviewForm(ModelForm):
    review = CharField(
        widget=Textarea(attrs={"placeholder": "Write your  review"}),
    )
    rating = ChoiceField(
        choices=Rating.choices,
        widget=Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = ProductReview
        fields = ["review", "rating"]


# class NowPaymentForm(ModelForm):
#     pay_currency = ChoiceField(choices=[])
#     order = 
