from django.urls import path

from acctmarket2.applications.users.views import (accountant_account,
                                                  administrator_account,
                                                  content_manager_account,
                                                  customer_support_reps,
                                                  customers_account,
                                                  dashboard_view, user_admin,
                                                  user_detail_view,
                                                  user_redirect_view,
                                                  user_update_view)

app_name = "users"
urlpatterns = [
    path(
        "signup/adminstrator-signup",
        view=administrator_account,
        name="administrator_account",
    ),
    path("dashboard", view=dashboard_view, name="dashboard_view"),
    path(
        "signup/content-manager",
        view=content_manager_account,
        name="content_manager_account",
    ),
    path(
        "signup/accountant", view=accountant_account,
        name="accountant_account"),
    path(
        "signup/customer-support",
        view=customer_support_reps,
        name="customer_support_reps",
    ),
    path("signup/customer", view=customers_account, name="customers_account"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("register-admin", view=user_admin, name="user_admin")
]
