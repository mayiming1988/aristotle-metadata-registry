from aristotle_mdr import perms
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.custom_fields import models as cf_models
from aristotle_mdr.contrib.slots import models as slots_models
from aristotle_dse import models as dse_models
from django.db.models import Model
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from aristotle_mdr.contrib.links import models as link_models
from aristotle_mdr.contrib.aristotle_backwards import models as backwards_models

import logging

logger = logging.getLogger(__name__)


class AristotleResolver(object):

    # allowed models that are not concepts:
    allowed_models = [link_models.LinkEnd, link_models.Link, mdr_models.OrganizationRecord, backwards_models.RepresentationClass]
    @classmethod
    def resolver(cls, attname, default_value, root, info, **args):
        retval = getattr(root, attname, default_value)

        # If object is a django model
        if isinstance(retval, Model):

            if isinstance(retval, mdr_models._concept):
                # Use user_can_view to determine if we display
                if perms.user_can_view(info.context.user, retval):
                    return retval
                else:
                    return None

            if isinstance(retval, mdr_models.aristotleComponent):
                # Use user_can_view to determine if we display
                if perms.user_can_view(info.context.user, retval):
                    return retval
                else:
                    return None

            if isinstance(retval, mdr_models.RegistrationAuthority):
                if retval.is_visible:
                    return retval
                else:
                    return None

            if type(retval) in cls.allowed_models:
                return retval

            return None

        elif isinstance(retval, Manager):
            # Need this for when related manager is returned when querying object.related_set
            # Can safely return restricted queryset
            queryset = retval.get_queryset()

            # We need to check permissions for Organizations depending on the authentication of the user:
            if queryset.model == mdr_models.RecordRelation:
                return queryset

            if queryset.model == slots_models.Slot:
                instance = getattr(retval, 'instance', None)
                if instance:
                    return slots_models.Slot.objects.get_item_allowed(instance, info.context.user)
                else:
                    return queryset.visible(info.context.user)

            if queryset.model == cf_models.CustomValue:
                instance = getattr(retval, 'instance', None)
                if instance:
                    return cf_models.CustomValue.objects.get_item_allowed(instance, info.context.user)
                else:
                    return queryset.visible(info.context.user)

            if hasattr(queryset, 'visible'):
                return queryset.visible(info.context.user)

            if queryset.model in (link_models.Link, link_models.LinkEnd):
                return queryset

            if issubclass(queryset.model, mdr_models.aristotleComponent):
                return queryset

            return queryset.none()

        elif isinstance(retval, QuerySet):
            # In case a queryset is returned
            if hasattr(retval, 'visible'):
                return retval.visible(info.context.user)
            if issubclass(retval.model, mdr_models.aristotleComponent):
                return retval

            return retval.none()

        return retval

    def __call__(self, *args, **kwargs):
        return self.__class__.resolver(*args, **kwargs)


aristotle_resolver = AristotleResolver()


class RegistrationAuthorityResolver(AristotleResolver):
    pass


class ValueDomainResolver(AristotleResolver):
    @classmethod
    def resolver(cls, attname, default_value, root, info, **args):
        retval = getattr(root, attname, default_value)
        logger.debug(str([
            type(retval), isinstance(retval, QuerySet)
        ]))
        if root.can_view(info.context.user):
            if isinstance(retval, Manager) and issubclass(retval.model, mdr_models.AbstractValue):
                return retval.get_queryset()
            if isinstance(retval, QuerySet) and issubclass(retval.model, mdr_models.AbstractValue):
                return retval
        return super().resolver(attname, default_value, root, info, **args)


class DataSetSpecificationResolver(AristotleResolver):
    @classmethod
    def resolver(cls, attname, default_value, root, info, **args):
        retval = getattr(root, attname, default_value)
        logger.debug(str([
            retval, type(retval), isinstance(retval, QuerySet)
        ]))
        if root.can_view(info.context.user):
            if isinstance(retval, Manager) and issubclass(retval.model, dse_models.DSSInclusion):
                return retval.get_queryset()
            if isinstance(retval, QuerySet) and issubclass(retval.model, dse_models.DSSInclusion):
                return retval
        return super().resolver(attname, default_value, root, info, **args)


class DSSInclusionResolver(AristotleResolver):
    pass
