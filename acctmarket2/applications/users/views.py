from allauth.account.utils import send_email_confirmation
from allauth.account.views import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (DetailView, RedirectView, TemplateView,
                                  UpdateView)
from django.views.generic.edit import CreateView

from acctmarket2.applications.ecommerce.models import CartOrder
from acctmarket2.applications.users.forms import (CustomSignupForm,
                                                  CustomUserCreationForm)
from acctmarket2.applications.users.models import (
    Account, Accountant, Administrator, ContentManager, Customer,
    CustomerSupportRepresentative, User)


class CustomSignupView(SignupView):
    form_class = CustomSignupForm


custom_signup_views = CustomSignupView.as_view()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name", "country", "phone_no", "email"]
    success_message = _("Information successfully updated")
    template_name = "account/user_detail.html"

    def get_success_url(self):
        # for mypy to know that the user is authenticated
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("homeapp:home")


user_redirect_view = UserRedirectView.as_view()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = CartOrder.objects.filter(user=self.request.user)

        context["orders"] = orders

        return context


dashboard_view = DashboardView.as_view()


class ContentManagerAccount(SignupView):
    form_class = CustomSignupForm
    template_name = "account/content_manager.html"

    def form_valid(self, form):
        try:
            user = form.save(self.request)
            expertise_area = form.cleaned_data.get("expertise_area")

            account, created = Account.objects.get_or_create(owner=user)
            ContentManager.objects.create(
                user=user,
                account=account,
                expertise_area=expertise_area,
            )

            send_email_confirmation(self.request, user)
            return HttpResponseRedirect("/accounts/confirm-email/")
        except ValueError as e:                 # noqa
            form.add_error(None, "The provided email address is not valid or already in use.")    # noqa
            return self.form_invalid(form)
        except (DatabaseError, ValidationError) as e:
            form.add_error(None, f"An error occurred: {e!s}")
            return self.form_invalid(form)


content_manager_account = ContentManagerAccount.as_view()


class AccountantAccount(SignupView):
    form_class = CustomSignupForm
    template_name = "account/accountant_signup.html"

    def form_valid(self, form):
        try:
            user = form.save(self.request)
            financial_software_used = form.cleaned_data.get("financial_software_used")  # noqa

            account, created = Account.objects.get_or_create(owner=user)
            Accountant.objects.create(
                user=user,
                account=account,
                financial_software_used=financial_software_used,
            )

            send_email_confirmation(self.request, user)
            return HttpResponseRedirect("/accounts/confirm-email/")
        except ValueError as e:      # noqa
            form.add_error(
                None,
                "The provided email address is not valid or already in use."
            )
            return self.form_invalid(form)
        except (DatabaseError, ValidationError) as e:
            form.add_error(None, f"An error occurred: {e!s}")
            return self.form_invalid(form)


accountant_account = AccountantAccount.as_view()


class AdministratorAccount(SignupView):
    form_class = CustomSignupForm
    template_name = "account/administrator.html"

    def form_valid(self, form):
        user = form.save(self.request)  # Use form.save() to get the user instance     # noqa
        department = form.cleaned_data.get("department")

        # Get or create the associated account for the user
        account, created = Account.objects.get_or_create(owner=user)

        # Create the Administrator instance with the associated account
        Administrator.objects.create(
            user=user, account=account, department=department)

        # Send email confirmation
        send_email_confirmation(self.request, user)

        return HttpResponseRedirect(
            "/accounts/confirm-email/",
        )  # Redirect after successful signup


administrator_account = AdministratorAccount.as_view()


class CustomerSupportRepresentativeAccount(SignupView):
    form_class = CustomSignupForm
    template_name = "account/customer_reps.html"

    def form_valid(self, form):
        try:
            user = form.save(self.request)
            department = form.cleaned_data.get("department")

            account, created = Account.objects.get_or_create(owner=user)
            CustomerSupportRepresentative.objects.create(
                user=user,
                account=account,
                department=department,
            )

            send_email_confirmation(self.request, user)
            return HttpResponseRedirect("/accounts/confirm-email/")
        except ValueError as e:                       # noqa
            # Handle the case where the email address is causing a ValueError
            form.add_error(None, "The provided email address is not valid or already in use.")           # noqa
            return self.form_invalid(form)
        except (DatabaseError, ValidationError) as e:
            form.add_error(None, f"An error occurred: {e!s}")
            return self.form_invalid(form)


customer_support_reps = CustomerSupportRepresentativeAccount.as_view()


class CustomerAccount(SignupView):
    form_class = CustomSignupForm
    template_name = "account/customer_account.html"

    def form_valid(self, form):
        try:
            user = form.save(self.request)
            account, created = Account.objects.get_or_create(owner=user)
            Customer.objects.create(
                user=user,
                account=account,
            )

            send_email_confirmation(self.request, user)
            return HttpResponseRedirect("/accounts/confirm-email/")
        except ValueError as e:                               # noqa
            # Handle the case where the email address is causing a ValueError
            form.add_error(None, "The provided email address is not valid or already in use.")     # noqa
            return self.form_invalid(form)
        except (DatabaseError, ValidationError) as e:
            form.add_error(None, f"An error occurred: {e!s}")
            return self.form_invalid(form)


customers_account = CustomerAccount.as_view()


class SuperuserSignupView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "account/superuser_signup.html"
    success_url = reverse_lazy('admin:login')

    def form_valid(self, form):
        # Set the necessary fields for superuser
        form.instance.is_staff = True
        form.instance.is_superuser = True
        return super().form_valid(form)


superuser = SuperuserSignupView.as_view()
