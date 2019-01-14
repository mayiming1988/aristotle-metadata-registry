from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import uuid

from model_utils.models import TimeStampedModel
from ckeditor_uploader.fields import RichTextUploadingField as RichTextField

from aristotle_mdr.fields import (
    ConceptForeignKey,
    ShortTextField,
)

from aristotle_mdr.managers import (
    MetadataItemManager,
    ManagedItemQuerySet,
)


class baseAristotleObject(TimeStampedModel):
    uuid = models.UUIDField(
        help_text=_("Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between registries"),
        unique=True, default=uuid.uuid1, editable=False, null=False
    )
    name = ShortTextField(
        help_text=_("The primary name used for human identification purposes.")
    )
    definition = RichTextField(
        _('definition'),
        help_text=_("Representation of a concept by a descriptive statement "
                    "which serves to differentiate it from related concepts. (3.2.39)")
    )
    objects = MetadataItemManager()

    class Meta:
        # So the url_name works for items we can't determine
        verbose_name = "item"
        # Can't be abstract as we need unique app wide IDs.
        abstract = True

    def was_modified_very_recently(self):
        return self.modified >= (
            timezone.now() - datetime.timedelta(seconds=VERY_RECENTLY_SECONDS)
        )

    def was_modified_recently(self):
        return self.modified >= timezone.now() - datetime.timedelta(days=1)

    was_modified_recently.admin_order_field = 'modified'  # type: ignore
    was_modified_recently.boolean = True  # type: ignore
    was_modified_recently.short_description = 'Modified recently?'  # type: ignore

    def description_stub(self):
        from django.utils.html import strip_tags
        d = strip_tags(self.definition)
        if len(d) > 150:
            d = d[0:150] + "..."
        return d

    def __str__(self):
        return "{name}".format(name=self.name)

    # Defined so we can access it during templates.
    @classmethod
    def get_verbose_name(cls):
        return cls._meta.verbose_name.title()

    @classmethod
    def get_verbose_name_plural(cls):
        return cls._meta.verbose_name_plural.title()

    def can_edit(self, user):
        # This should always be overridden
        raise NotImplementedError  # pragma: no cover

    def can_view(self, user):
        # This should always be overridden
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def meta(self):
        # I know what I'm doing, get out the way.
        return self._meta


class ManagedItem(baseAristotleObject):
    """Managed items can be published, but not registered"""
    class Meta:
        abstract = True

    objects = ManagedItemQuerySet.as_manager()

    publication_details = GenericRelation('aristotle_mdr_publishing.PublicationRecord')
    stewardship_organisation = models.ForeignKey(
        'aristotle_mdr.StewardOrganisation', to_field="uuid",
        null=False,
        related_name="managed_items"
    )
    # workgroup = models.ForeignKey('aristotle_mdr.Workgroup', related_name="managed_items", null=True, blank=True)

    def can_edit(self, user):
        return user.is_superuser

    def can_view(self, user):
        return True

    @property
    def item(self):
        return self

    def get_absolute_url(self):
        return reverse(
            "aristotle_mdr:view_managed_item",
            # args=[self.slug],
            kwargs={
                "model_slug": self._meta.model.__name__.lower(),
                "iid": self.pk
            }
        )


class aristotleComponent(models.Model):
    class Meta:
        abstract = True

    ordering_field = 'order'

    def can_edit(self, user):
        return self.parentItem.can_edit(user)

    def can_view(self, user):
        return self.parentItem.can_view(user)


class discussionAbstract(TimeStampedModel):
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def edited(self):
        return self.created != self.modified


class AbstractValue(aristotleComponent):
    """
    Implementation note: Not the best name, but there will be times to
    subclass a "value" when its not just a permissible value.
    """

    class Meta:
        abstract = True
        ordering = ['order']
    value = ShortTextField(  # 11.3.2.7.2.1 - Renamed from permitted value for abstracts
        help_text=_("the actual value of the Value")
    )
    meaning = ShortTextField(  # 11.3.2.7.1
        help_text=_("A textual designation of a value, where a relation to a Value meaning doesn't exist")
    )
    value_meaning = models.ForeignKey(  # 11.3.2.7.1
        'ValueMeaning',
        blank=True,
        null=True,
        help_text=_('A reference to the value meaning that this designation relates to')
    )
    # Below will generate exactly the same related name as django, but reversion-compare
    # needs an explicit related_name for some actions.
    valueDomain = ConceptForeignKey(
        'ValueDomain',
        related_name="%(class)s_set",
        help_text=_("Enumerated Value Domain that this value meaning relates to"),
        verbose_name='Value Domain'
    )
    order = models.PositiveSmallIntegerField("Position")
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Date at which the value became valid')
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Date at which the value ceased to be valid')
    )

    def __str__(self):
        return "%s: %s - %s" % (
            self.valueDomain.name,
            self.value,
            self.meaning
        )

    @property
    def parentItem(self):
        return self.valueDomain

    @property
    def parentItemId(self):
        return self.valueDomain_id


class DedBaseThrough(models.Model):
    """
    Abstract Class for Data Element Derivation Manay to Many through tables with ordering
    """

    data_element_derivation = models.ForeignKey('DataElementDerivation', on_delete=models.CASCADE)
    data_element = models.ForeignKey('DataElement', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField("Position")

    class Meta:
        abstract = True
        ordering = ['order']

