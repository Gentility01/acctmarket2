import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "acctmarket2.applications.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import acctmarket2.applications.users.signals  # noqa: F401
