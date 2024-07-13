from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import BooleanField, CharField, EmailField
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import (Accountant, Administrator, AffiliatePartner,
                     ContentManager, CustomerSupportRepresentative,
                     DigitalGoodsDistribution, HelpDeskTechnicalSupport,
                     LiveChatSupport, MarketingAndSales, User)


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class CustomSignupBaseForm(SignupForm):
    """
    Base form for custom signup forms.
    """

    name = CharField(max_length=255, label="Name", required=True)
    phone_no = CharField(max_length=20, label="Phone number", required=False)
    terms = BooleanField(required=True,
                         label="I agree to the Terms and Conditions")
    country = CountryField(blank_label="(select country)").formfield(
        widget=CountrySelectWidget(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form fields
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your name"},
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your email"},
        )
        self.fields["phone_no"].widget.attrs.update(
            {"class": "form-control",
             "placeholder": "Enter your phone number"},
        )
        self.fields["country"].widget.attrs.update(
            {"class": "form-control"},
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password"},
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm your password"},
        )

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get("name")
        user.phone_no = self.cleaned_data.get("phone_no")
        user.country = self.cleaned_data.get("country")
        user.save()
        return user


class UserSignupForm(CustomSignupBaseForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class CustomSignupForm(CustomSignupBaseForm):
    USER_TYPES = {
        "administrator": Administrator,
        "customer_support_representative": CustomerSupportRepresentative,
        "content_manager": ContentManager,
        "marketing_and_sales": MarketingAndSales,
        "accountant": Accountant,
        "help_desk_technical_support": HelpDeskTechnicalSupport,
        "live_chat_support": LiveChatSupport,
        "affiliate_partner": AffiliatePartner,
        "digital_goods_distribution": DigitalGoodsDistribution,
    }

    user_type = CharField(max_length=50, required=True)
    expertise_area = CharField(
        max_length=255,
        required=False,
    )  # Used in ContentManagerAccount
    financial_software_used = CharField(
        max_length=100,
        required=False,
    )  # Used in AccountantAccount

    class InvalidUserTypeValidationError(ValidationError):
        pass

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        if user_type not in self.USER_TYPES:
            error_message = "Invalid user type"
            raise self.InvalidUserTypeValidationError(error_message)
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        profile_data = self.cleaned_data

        profile_class = self.USER_TYPES.get(profile_data["user_type"])
        if profile_class:
            profile_instance = profile_class(user=user)
            if "expertise_area" in profile_data:
                profile_instance.expertise_area = profile_data["expertise_area"]                   # noqa
            if "financial_software_used" in profile_data:
                profile_instance.financial_software_used = profile_data[
                    "financial_software_used"
                ]
            profile_instance.save()

        return user


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when a user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "name", "phone_no", "country")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "name", "phone_no", "country")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
