from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.fields import (
    ConceptForeignKey,
    ShortTextField,
    ConceptManyToManyField,
)


class Collection(TimeStampedModel):
    """A collection of metadata belonging to a Stewardship Organisation"""

    stewardship_organisation = models.ForeignKey(
        'aristotle_mdr.StewardOrganisation', to_field="uuid", null=False,
    )
    name = ShortTextField(
        help_text=_("The name of the group.")
    )
    description = MDR.RichTextField(
        _('description'),
        blank=True
    )

    metadata = ConceptManyToManyField('aristotle_mdr._concept', blank=True)
    parent_collection = models.ForeignKey('self', null=True)

    def get_absolute_url(self):
        return reverse(
            "aristotle_mdr:stewards:group:collection_detail_view",
            args=[self.stewardship_organisation.slug, self.pk]
        )


# class CollectionEntry(models.Model):
#     order = models.PositiveSmallIntegerField("Order")
#     collection = ConceptForeignKey(Collection)
#     metadata = ConceptForeignKey('aristotle_mdr._concept', blank=True, null=True)

