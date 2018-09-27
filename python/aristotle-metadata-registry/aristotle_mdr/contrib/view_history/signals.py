import django.dispatch
from django.contrib.auth import get_user_model
from aristotle_mdr.contrib.async_signals.utils import safe_object

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


metadata_item_viewed = django.dispatch.Signal(providing_args=["user"])
User = get_user_model()


def item_viewed_action(message):
    instance = safe_object(message)
    if not instance:
        return
    from .models import UserViewHistory

    UserViewHistory.objects.create(
        concept=instance,
        user=User.objects.get(pk=message['user'])
    )
