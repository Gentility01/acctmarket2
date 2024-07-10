from django.db.models.signals import post_save
from django.dispatch import receiver

from acctmarket2.applications.ecommerce.models import CartOrderItems


@receiver(post_save, sender=CartOrderItems)
def assign_unique_key(sender, instance, created, **kwargs):
    """
    Signal to handle the assignment of unique keys
    after an order item is created.

    Args:
        sender (Model): The model class that sent the signal.
        instance (CartOrderItems): The instance of the model that was saved.
        created (bool): Whether this instance is being created.
        kwargs (dict): Additional keyword arguments.
    """
    if created:
        # This method is already handled in the service layer.
        # Just demonstrating how you could use signals for side effects.
        pass
