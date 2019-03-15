from typing import Iterable
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.module_loading import import_string
from aristotle_mdr.utils import fetch_aristotle_settings
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from aristotle_mdr.contrib.reviews.const import REVIEW_STATES
from aristotle_mdr.utils.utils import is_postgres
from aristotle_mdr.constants import visibility_permission_choices

from django.contrib.contenttypes.models import ContentType


class PublishedMixin(object):

    @property
    def is_published_public(self):
        from aristotle_mdr.models import _concept
        return Q(
            publication_details__permission=visibility_permission_choices.public,
            publication_details__publication_date__lte=timezone.now(),
        )

    @property
    def is_published_auth(self):
        return Q(
            publication_details__permission=visibility_permission_choices.auth,
            publication_details__publication_date__lte=timezone.now()
        )


class UtilsManager(models.Manager):
    """Manager with extra util functions"""

    def bulk_delete(self, objects: Iterable[models.Model]):
        if isinstance(objects, models.QuerySet):
            objects.delete()
        else:
            ids = [o.id for o in objects]
            qs = self.get_queryset().filter(id__in=ids)
            qs.delete()


class MetadataItemQuerySet(InheritanceQuerySet):
    pass


class MetadataItemManager(InheritanceManager, UtilsManager):
    def get_queryset(self):
        from django.conf import settings

        qs = MetadataItemQuerySet(self.model, using=self._db)
        if hasattr(settings, 'FORCE_METADATAMANAGER_FILTER'):
            qs = qs.filter(*import_string(settings.FORCE_METADATAMANAGER_FILTER)())
        return qs


class WorkgroupQuerySet(MetadataItemQuerySet):
    def visible(self, user):
        if user.is_anonymous():
            return self.none()
        if user.is_superuser:
            return self.all()
        # TODO: Figure out how to make admins of the steward org able to view using this queryset
        return user.profile.workgroups


class RegistrationAuthorityQuerySet(models.QuerySet):
    def visible(self, user):
        return self.all()


class ConceptQuerySet(PublishedMixin, MetadataItemQuerySet):

    def visible(self, user):
        """
        Returns a queryset that returns all items that the given user has
        permission to view.

        It is **chainable** with other querysets. For example, both of these
        will work and return the same list::

            ObjectClass.objects.filter(name__contains="Person").visible()
            ObjectClass.objects.visible().filter(name__contains="Person")
        """
        need_distinct = False  # Wether we need to add a distinct
        from aristotle_mdr.models import StewardOrganisation

        if user is None or user.is_anonymous:
            return self.public()
        if user.is_superuser:
            return self.all()
        q = Q(_is_public=True)

        if user.is_active:
            # User can see everything they've made.
            q |= Q(submitter=user)
            # User can see everything in their workgroups.
            q |= Q(workgroup__in=user.profile.workgroups)
            # q |= Q(workgroup__user__profile=user)
            registrar_count = user.profile.registrar_count
            if registrar_count > 1:
                # If a user is a registrar in multiple ras it is possible for
                # the query to return duplicates
                need_distinct = True
            if registrar_count > 0:
                # Registars can see items they have been asked to review
                q |= Q(
                    Q(rr_review_requests__registration_authority__registrars__profile__user=user) &
                    ~Q(rr_review_requests__status=REVIEW_STATES.revoked)
                )
                # Registars can see items that have been registered in their registration authority
                q |= Q(
                    Q(statuses__registrationAuthority__registrars__profile__user=user)
                )

        q |= self.is_published_public
        q |= self.is_published_auth

        q &= ~Q(stewardship_organisation__state=StewardOrganisation.states.hidden)

        if not need_distinct:
            return self.filter(q)
        else:
            return self.filter(q).distinct()

    def editable(self, user):
        """
        Returns a queryset that returns all items that the given user has
        permission to edit.

        It is **chainable** with other querysets. For example, both of these
        will work and return the same list::

            ObjectClass.objects.filter(name__contains="Person").editable()
            ObjectClass.objects.editable().filter(name__contains="Person")
        """
        from aristotle_mdr.models import StewardOrganisation
        if user.is_superuser:
            return self.all()
        if user.is_anonymous():
            return self.none()
        q = Q()

        # User can edit everything they've made thats not locked
        q |= Q(submitter=user, _is_locked=False)

        is_submitter = user.submitter_in.exists()
        is_steward = user.steward_in.exists()

        if is_submitter or is_steward:
            if is_submitter:
                q |= Q(_is_locked=False, workgroup__submitters__profile__user=user)
            if is_steward:
                q |= Q(workgroup__stewards__profile__user=user)
        return self.filter(
            q &
            ~Q(stewardship_organisation__state=StewardOrganisation.states.hidden)
        )

    def public(self):
        """
        Returns a list of public items from the queryset.

        This is a chainable query set, that filters on items which have the
        internal `_is_public` flag set to true.

        Both of these examples will work and return the same list::

            ObjectClass.objects.filter(name__contains="Person").public()
            ObjectClass.objects.public().filter(name__contains="Person")
        """
        from aristotle_mdr.models import StewardOrganisation
        return self.filter(
            Q(self.is_published_public | Q(_is_public=True)) &
            ~Q(stewardship_organisation__state=StewardOrganisation.states.hidden)
        )

    def with_related(self):
        related = self.model.related_objects
        if related:
            return self.select_related(*related)
        return self

    def __contains__(self, item):
        from aristotle_mdr.models import _concept

        if not issubclass(type(item), _concept):
            return False
        else:
            return self.all().filter(pk=item.concept.pk).exists()


class ConceptManager(MetadataItemManager):
    """
    The ``ConceptManager`` is the default object manager for ``concept`` and
    ``_concept`` items, and extends from the django-model-utils
    ``InheritanceManager``.

    It provides access to the ``ConceptQuerySet`` to allow for easy
    permissions-based filtering of ISO 11179 Concept-based items.
    """
    def get_queryset(self):
        from django.conf import settings

        qs = ConceptQuerySet(self.model, using=self._db)
        if hasattr(settings, 'FORCE_CONCEPTMANAGER_FILTER'):
            qs = qs.filter(*import_string(settings.FORCE_CONCEPTMANAGER_FILTER)())
        return qs
        # return ConceptQuerySet(self.model)

    def __getattr__(self, attr, *args):
        if attr in ['editable', 'visible', 'public']:
            return getattr(self.get_queryset(), attr, *args)
        else:
            return getattr(self.__class__, attr, *args)


class ReviewRequestQuerySet(models.QuerySet):
    def visible(self, user):
        """
        Returns a queryset that returns all reviews that the given user has
        permission to view.

        It is **chainable** with other querysets.
        """
        needs_distinct = False

        if user.is_superuser:
            return self.all()
        if user.is_anonymous():
            return self.none()
        q = Q(requester=user)  # Users can always see reviews they requested
        if user.profile.is_registrar:
            needs_distinct = True
            # Registars can see reviews for the registration authority
            q |= Q(
                Q(registration_authority__registrars__profile__user=user) &
                ~Q(status=REVIEW_STATES.revoked)
            )

        if needs_distinct:
            return self.filter(q).distinct()

        return self.filter(q)


class StatusQuerySet(models.QuerySet):
    def visible(self, user):
        """
        Returns a queryset that returns all statuses that the given user has
        permission to view.

        It is **chainable** with other querysets.
        """
        return self.all()

    def valid(self):
        return self.valid_at_date(timezone.now().date())

    def valid_at_date(self, when=timezone.now().date()):
        registered_before_now = Q(registrationDate__lte=when)
        registration_still_valid = (
            Q(until_date__gte=when) |
            Q(until_date__isnull=True)
        )

        return self.filter(
            registered_before_now & registration_still_valid
        )

    def current(self, when=timezone.now()):
        """
        Returns a queryset that returns the most up to date statuses

        It is **chainable** with other querysets.
        """
        if hasattr(when, 'date'):
            when = when.date()

        states = self.valid_at_date(when)
        states = states.order_by("registrationAuthority", "-registrationDate", "-created")

        from django.db import connection
        if connection.vendor == 'postgresql':
            states = states.distinct('registrationAuthority')
        else:
            current_ids = []
            seen_ras = []
            for s in states:
                ra = s.registrationAuthority
                if ra not in seen_ras:
                    current_ids.append(s.pk)
                    seen_ras.append(ra)
            # We hit again so we can return this as a queryset
            states = states.filter(pk__in=current_ids)

        return states.select_related('registrationAuthority')


class SupersedesManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(proposed=False)


class ProposedSupersedesManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(proposed=True)


class ManagedItemQuerySet(PublishedMixin, models.QuerySet):
    def visible(self, user):
        """
        Returns a queryset that returns all managed items that the given user has
        permission to view.

        It is **chainable** with other querysets.
        """
        if user.is_superuser:
            return self.all()

        q = self.is_published_public
        if user.is_anonymous():
            return self.filter(q)

        q |= self.is_published_auth
        # q |= Q(
        #     workgroup__in=user.profile.workgroups,
        #     publication_details__permission=visibility_permission_choices.workgroup
        # )

        return self.filter(q)

    def editable(self, user):
        """
        Returns a queryset that returns all managed items that the given user has
        permission to edit.

        It is **chainable** with other querysets.
        """
        if user.is_superuser:
            return self.all()
        if user.is_anonymous():
            return self.none()

        from aristotle_mdr.models import StewardOrganisation

        q = Q(
            stewardship_organisation__members__user=user,
            stewardship_organisation__members__role__in=[
                StewardOrganisation.roles.admin, StewardOrganisation.roles.steward
            ]
        )

        return self.filter(q)
