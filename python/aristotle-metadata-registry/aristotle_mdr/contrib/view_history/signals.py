from datetime import timedelta
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.utils.timezone import now

from aristotle_mdr.contrib.async_signals.utils import safe_object

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


metadata_item_viewed = Signal(providing_args=["user"])
User = get_user_model()


def item_viewed_action(message):
    instance = safe_object(message)
    if not instance:
        return
    if message['user'] is None:
        # Don't accept anonymous users.
        return
    try:
        user = User.objects.get(pk=message['user'])
    except:
        # TODO: Maybe log this
        # If we don't get a valid user, then don't try and assign to them.
        return
    recently = now() - timedelta(minutes=30)
    if user.recently_viewed_metadata.filter(view_date__gt=recently, concept=instance).exists():
        return

    from .models import UserViewHistory

    UserViewHistory.objects.create(
        concept=instance,
        user=user
    )
