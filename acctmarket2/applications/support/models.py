import auto_prefetch
from django.conf import settings
from django.db.models import SET_NULL, CharField, TextField

from acctmarket2.utils.choices import Ticket
from acctmarket2.utils.models import TitleTimeBasedModel

# Create your models here.


class Ticket(TitleTimeBasedModel):
    customer = auto_prefetch.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        related_name="tickets",
        null=True,
        default="",
    )
    assigned_to = auto_prefetch.ForeignKey(
        "users.CustomerSupportRepresentative",
        on_delete=SET_NULL,
        null=True,
        default="",
        related_name="tickets",
    )
    description = TextField()
    status = CharField(max_length=20, choices=Ticket.choices, default=Ticket.OPEN)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return self.title


class Response(TitleTimeBasedModel):
    ticket = auto_prefetch.ForeignKey(
        Ticket,
        on_delete=SET_NULL,
        null=True,
        default="",
        related_name="responses",
    )
    user = auto_prefetch.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        null=True,
        default="",
        related_name="responses",
    )
    messages = TextField()

    class Meta:
        verbose_name = "Response"
        verbose_name_plural = "Responses"

    def __str__(self):
        return f"Response by {self.user.email} on {self.ticket.title}"


class FrequestAskQuestion(TitleTimeBasedModel):
    content = TextField()

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.title
