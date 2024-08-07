# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views import defaults as default_views

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path("", include(
        "acctmarket2.applications.home.urls", namespace="homeapp")
    ),
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include(
        "acctmarket2.applications.users.urls", namespace="users")
    ),
    #  ecomercce manaement
    path(
        "ecommerce/",
        include(
            "acctmarket2.applications.ecommerce.urls", namespace="ecommerce"
        ),
    ),
    # blog management
    path("blog/", include(
        "acctmarket2.applications.blog.urls", namespace="blog")
    ),
    # support management
    path(
        "support/",
        include("acctmarket2.applications.support.urls", namespace="support"),
    ),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("ckeditor/", include("ckeditor_uploader.urls")),
    # ...
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket
    # development
    urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns  # noqa
