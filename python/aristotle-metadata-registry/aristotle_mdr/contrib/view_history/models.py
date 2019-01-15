from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


from aristotle_mdr import models as MDR
from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.contrib.async_signals.utils import fire
from .signals import metadata_item_viewed


class UserViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="recently_viewed_metadata")
    concept = ConceptForeignKey(MDR._concept, related_name='user_view_history')
    view_date = models.DateTimeField(
        default=now,
        help_text=_("When the item was viewed")
    )


@receiver(metadata_item_viewed)
def item_viewed(sender, *args, **kwargs):
    fire("signals.item_viewed_action", namespace="aristotle_mdr.contrib.view_history", obj=sender, **kwargs)
