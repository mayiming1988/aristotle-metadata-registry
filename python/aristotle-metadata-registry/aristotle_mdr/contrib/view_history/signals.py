from datetime import timedelta
from django.dispatch import receiver, Signal
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from aristotle_mdr.contrib.async_signals.utils import fire
from aristotle_mdr.contrib.async_signals.utils import safe_object
from aristotle_mdr.contrib.view_history.models import UserViewHistory

User = get_user_model()
metadata_item_viewed = Signal(providing_args=['user'])


def item_viewed_action(message):
    instance = safe_object(message)

    # Don't accept anonymous users.
    if message['user'] is not None:

        user = User.objects.get(pk=message['user'])
        recently = now() - timedelta(minutes=30)

        # Create history if a recent one doesn't exist
        if not user.recently_viewed_metadata.filter(view_date__gt=recently, concept=instance).exists():

            UserViewHistory.objects.create(
                concept=instance,
                user=user
            )


@receiver(metadata_item_viewed)
def item_viewed(sender, *args, **kwargs):
    fire("signals.item_viewed_action", namespace="aristotle_mdr.contrib.view_history", obj=sender, **kwargs)
