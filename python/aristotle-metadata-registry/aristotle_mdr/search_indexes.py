import haystack.indexes as indexes

from django.db.models import Q
from django.template import TemplateDoesNotExist, loader
from django.template import loader
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from aristotle_mdr.contrib.reviews.const import REVIEW_STATES
import aristotle_mdr.contrib.stewards.models as contrib_models
from aristotle_mdr.constants import visibility_permission_choices
import aristotle_mdr.models as models

import logging
logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

BASE_RESTRICTION = {
    0: 'Public',
    1: 'Locked',
    2: 'Unlocked',
}
RESTRICTION: dict = {}
# reverse the dictionary to make two-way look ups easier
RESTRICTION.update([(k, v) for k, v in BASE_RESTRICTION.items()])
RESTRICTION.update([(str(k), v) for k, v in BASE_RESTRICTION.items()])
RESTRICTION.update([(v, k) for k, v in BASE_RESTRICTION.items()])

registered_indexes: list = []

SEARCH_CATEGORIES = Choices(
    ('all', _("All")),
    ('collaboration', _("Issues & Discussions")),
    ('data', _("Data")),
    ('help', _("Help")),
    ('metadata', _("Metadata")),
    ('references', _("References")),
    # ('other', _("Other")),
)


class ConceptFallbackCharField(indexes.CharField):
    def prepare_template(self, obj):
        try:
            return super().prepare_template(obj)
        except TemplateDoesNotExist:
            logger.debug("No search template found for %s, using untyped fallback." % obj)
            t = loader.select_template(["search/indexes/aristotle_mdr/untyped_concept_text.txt"])
            return t.render({'object': obj})


class BaseObjectIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    category = indexes.CharField()
    modified = indexes.DateTimeField(model_attr='modified')
    created = indexes.DateTimeField(model_attr='created')
    name = indexes.CharField(model_attr='name', boost=1)
    facet_model_ct = indexes.IntegerField(faceted=True)
    django_ct_app_label = indexes.CharField()
    # Thanks ElasticSearch - https://github.com/django-haystack/django-haystack/issues/569
    name_sortable = indexes.CharField(model_attr='name', indexed=False, stored=True)
    # django_ct_model_name = indexes.CharField()
    # access = indexes.MultiValueField()
    rendered_badge = indexes.CharField(indexed=False)

    rendered_search_result = indexes.CharField(indexed=False)

    badge_template_name = "search/badges/base.html"
    search_category = SEARCH_CATEGORIES.all

    def prepare_django_ct_app_label(self, obj):
        return obj._meta.app_label

    def prepare_category(self, obj):
        return self.search_category

    def prepare_rendered_badge(self, obj):
        t = loader.get_template(self.badge_template_name)
        return t.render({'object': obj})

    def prepare_rendered_search_result(self, obj):
        t = loader.get_template(self.template_name)
        return t.render({'object': obj})

    def get_model(self):
        raise NotImplementedError  # pragma: no cover -- This should always be overridden

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(modified__lte=timezone.now())

    def prepare_facet_model_ct(self, obj):
        # We need to use the content type, as if we use text it gets stemmed wierdly
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        return ct.pk


class ConceptIndex(BaseObjectIndex):
    text = ConceptFallbackCharField(document=True, use_template=True)
    uuid = indexes.CharField(model_attr='uuid')
    statuses = indexes.MultiValueField(faceted=True)
    highest_state = indexes.IntegerField()
    ra_statuses = indexes.MultiValueField()
    registrationAuthorities = indexes.MultiValueField(faceted=True)
    workgroup = indexes.IntegerField(faceted=True)
    is_public = indexes.BooleanField()
    restriction = indexes.IntegerField(faceted=True)
    version = indexes.CharField(model_attr="version")
    submitter_id = indexes.IntegerField(model_attr="submitter_id", null=True)
    identifier = indexes.MultiValueField()
    namespace = indexes.MultiValueField()
    published_date_public = indexes.DateTimeField(null=True)
    stewardship_organisation = indexes.IntegerField(faceted=True, model_attr="stewardship_organisation__id")

    template_name = "search/searchItem.html"
    badge_template_name = "search/badges/metadata.html"

    rendered_badge = indexes.CharField(indexed=False)
    search_category = SEARCH_CATEGORIES.metadata

    # Preparation functions for conceptIndex

    def prepare_registrationAuthorities(self, obj):
        ras_stats = [str(s.registrationAuthority.id) for s in obj.current_statuses().all()]
        ras_reqs = [str(rr.registration_authority.id) for rr in obj.rr_review_requests.filter(~Q(status=REVIEW_STATES.revoked)).all()]

        return list(set(ras_stats + ras_reqs))

    def prepare_is_public(self, obj):
        return obj.is_public()

    def prepare_workgroup(self, obj):
        if obj.workgroup:
            return int(obj.workgroup.id)
        else:
            return -99

    def prepare_statuses(self, obj):
        # We don't remove duplicates as it should mean the more standard it is the higher it will rank
        states = [int(s.state) for s in obj.current_statuses().all()]
        if not states:
            states = ['-99']  # This is an unregistered item
        return states

    def prepare_highest_state(self, obj):
        # Include -99, so "unregistered" items get a value
        state = max([int(s.state) for s in obj.current_statuses().all()] + [-99])
        """
        We don't want retired or superseded ranking higher than standards during search
        as these are no longer "fit for purpose" so we'll place them below other
        states for the purposes of sorting in search.
        """
        if state == models.STATES.retired:
            state = -10
        elif state == models.STATES.superseded:
            state = -9
        return state

    def prepare_ra_statuses(self, obj):
        # This allows us to check a registration authority and a state simultaneously
        states = [
            "%s___%s" % (str(s.registrationAuthority.id), str(s.state)) for s in obj.current_statuses().all()
        ]
        return states

    def prepare_restriction(self, obj):
        if obj._is_public:
            return RESTRICTION['Public']
        elif obj._is_locked:
            return RESTRICTION['Locked']
        return RESTRICTION['Unlocked']

    def prepare_identifier(self, obj):
        identifiers = []
        for scoped_ident in obj.identifiers.all().select_related('namespace'):
            identifiers.append(
                '{}/{}/{}'.format(
                    scoped_ident.namespace.shorthand_prefix,
                    scoped_ident.identifier,
                    scoped_ident.version
                )
            )
        return identifiers

    def prepare_namespace(self, obj):
        return [ident.namespace.shorthand_prefix for ident in obj.identifiers.all().select_related('namespace')]

    def prepare_published_date_public(self, obj):
        record = obj.concept.publication_details.filter(permission=visibility_permission_choices.public).first()
        if record:
            return record.publication_date


class DiscussionIndex(BaseObjectIndex, indexes.Indexable):
    """ Index of Discussion posts """
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='title')
    name_sortable = indexes.CharField(model_attr='title', indexed=False, stored=True)
    discussion_body = indexes.CharField(model_attr='body')
    modified = indexes.DateTimeField(model_attr='modified')
    created = indexes.DateTimeField(model_attr='created')
    workgroup = indexes.IntegerField(faceted=True)

    rendered_search_result = indexes.CharField(indexed=False)

    template_name = "search/searchDiscussion.html"
    search_category = SEARCH_CATEGORIES.collaboration

    def prepare_rendered_search_result(self, discussion_post):
        """
        Pre-renders all the discussion search results to avoid hitting the database every search
        """
        t = loader.get_template(self.template_name)
        return t.render({'discussion_post': discussion_post})

    def prepare_workgroup(self, obj):
        return int(obj.workgroup.id)

    def get_model(self):
        return models.DiscussionPost

    def index_queryset(self, using=None):
        # When reindexing occurs
        return self.get_model().objects.filter(modified__lte=timezone.now())


class CollectionIndex(BaseObjectIndex, indexes.Indexable):
    """ Index of collections """
    text = indexes.CharField(document=True, use_template=True)
    stewardship_organisation = indexes.IntegerField(faceted=True, model_attr="stewardship_organisation__id")

    name = indexes.CharField(model_attr="name")
    description = indexes.CharField(model_attr="description")
    modified = indexes.DateTimeField(model_attr="modified")
    created = indexes.DateTimeField(model_attr="created")

    rendered_search_result = indexes.CharField(indexed=False)
    template_name = "search/searchCollection.html"
    search_category = SEARCH_CATEGORIES.references

    def get_model(self):
        return contrib_models.Collection

    def index_queryset(self, using=None):
        # When reindexing occurs
        return self.get_model().objects.filter(modified__lte=timezone.now())

    def prepare_rendered_search_result(self, collection):
        """
        Pre-renders all the collections to avoid hitting the database every search
        """
        t = loader.get_template(self.template_name)
        return t.render({'collection': collection})
