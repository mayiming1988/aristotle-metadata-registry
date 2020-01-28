from typing import Optional
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from django.conf import settings
from django.db.models import Q, Count, Model
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import six

from dal import autocomplete

from aristotle_mdr import models, perms
from aristotle_mdr.contrib.links.models import Relation
from aristotle_mdr.contrib.stewards.models import Collection
from comet.models import FrameworkDimension


class GenericAutocomplete(autocomplete.Select2QuerySetView):
    """
    Generic autocomplete view subclassed below
    Is not used as a view itself
    """
    model: Optional[Model] = None
    template_name: str = "autocomplete_light/item.html"

    def get_queryset(self):
        """Get queryset used to produce list
        Should be doing permission checks here"""
        raise NotImplementedError

    def text_filter_query(self, qs):
        """Filter query based on 'q' query param"""
        if self.q:
            return qs.filter(name__icontains=self.q)

        return qs

    def get_result_title(self, result):
        """Return the title of a result."""
        return six.text_type(result)

    def get_result_text(self, result):
        """Return the label of a result."""
        template = get_template(self.template_name)
        context = {"result": result, 'request': self.request}
        return template.render(context)

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        return [
            {
                'id': self.get_result_value(result),
                'title': self.get_result_title(result),
                'text': self.get_result_title(result),
                'body': self.get_result_text(result),
            } for result in context['object_list']
        ]


class GenericConceptAutocomplete(GenericAutocomplete):
    """
    Generic concept autocomplete view.
    Can be used to autocomplete any concept by app_label and model name
    """
    template_name = "autocomplete_light/concept.html"
    # Default model used if app_label and model_name are not supplied
    model = models._concept

    def get_concept_model(self):
        """Get concept model from url params"""
        app_name = self.kwargs.get('app_name', None)
        model_name = self.kwargs.get('model_name', None)
        if app_name and model_name:
            model = get_object_or_404(
                ContentType, app_label=app_name, model=model_name
            ).model_class()

            # Must be a model subclass, otherwise 403
            if not issubclass(model, models._concept):
                raise PermissionDenied

            return model

        # Default to filtering _concept's
        return self.model

    def get_queryset(self):
        model = self.get_concept_model()

        # Get public query parameter
        public = self.request.GET.get('public', '')
        # If we requested public objects, or are not authenticated
        if public or not self.request.user.is_authenticated:
            qs = model.objects.public()
        else:
            qs = model.objects.visible(self.request.user)

        # Filter by query
        if self.q:
            q = Q(name__icontains=self.q)
            q |= Q(uuid__iexact=self.q)
            if 'aristotle_mdr.contrib.identifiers' in settings.INSTALLED_APPS:
                q |= Q(identifiers__identifier__iexact=self.q)

            # If q is a number also query by pk
            if self.q.isdigit():
                q |= Q(pk=self.q)

            qs = qs.filter(q).order_by('name')
        return qs

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        return [
            {
                'id': self.get_result_value(result),
                'uuid': str(result.uuid),
                'title': self.get_result_title(result),
                'text': self.get_result_title(result),
                'body': self.get_result_text(result),
            } for result in context['object_list']
        ]


class RelationAutocomplete(GenericConceptAutocomplete):
    """Custom autocompletion for relations, with additional filtering"""
    model = Relation

    def get_queryset(self):
        """Filter on only the Relations that have at least one associated role"""
        qs = super().get_queryset()
        qs = qs.annotate(num_roles=Count('relationrole')).filter(num_roles__gt=0)
        return qs


class FrameworkDimensionsAutocomplete(GenericAutocomplete):
    """Autocomplete for framework dimension objects (these are not concepts)"""
    model = FrameworkDimension
    template_name = "autocomplete_light/framework_dimensions.html"

    def get_queryset(self):
        qs = self.model.objects.all().visible(self.request.user)
        qs = self.text_filter_query(qs)
        qs = qs.order_by('name')
        return qs


class CollectionAutocomplete(GenericAutocomplete):
    """Autocomplete for collection objects
    Used for selecting parent collection"""
    model = Collection
    template_name = 'autocomplete_light/collections.html'

    def dispatch(self, *args, **kwargs):
        self.so = get_object_or_404(models.StewardOrganisation, uuid=self.kwargs['souuid'])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        # Restrict to collections the user can manage
        qs = self.model.objects.all().editable(self.request.user, self.so)

        qs = self.text_filter_query(qs)
        qs = qs.order_by('name')

        # exclude by id if the query parameter is present
        if 'exclude' in self.request.GET:
            exclude = self.request.GET['exclude']
            qs = qs.exclude(pk=exclude)

        return qs


class UserAutocomplete(GenericAutocomplete):
    model = None
    template_name = "aristotle_mdr/actions/autocompleteUser.html"

    def get_queryset(self):
        self.model = get_user_model()

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        if not perms.user_can_query_user_list(self.request.user):
            raise PermissionDenied

        if self.q:
            qs = self.model.objects.filter(is_active=True).filter(
                Q(email__icontains=self.q) |
                Q(short_name__icontains=self.q) | Q(full_name__icontains=self.q)
            )
        else:
            if self.request.user.is_superuser:
                qs = self.model.objects.filter(is_active=True)
            else:
                qs = self.model.objects.none()

        return qs

    def get_result_text(self, result):
        """Return the label of a result."""

        template = get_template(self.template_name)
        result.highlight = {}
        for f in ['email', 'full_name']:
            field = getattr(result, f, None)
            if callable(field):
                field = field()
            if field and self.q.lower() in field.lower():
                index = field.lower().index(self.q.lower())
                offset = index + len(self.q)
                field = "%s<b><u>%s</u></b>%s" % (field[:index], field[index:offset], field[offset:])

            result.highlight[f] = field
        context = {"result": result, 'request': self.request}
        return template.render(context)

    def get_result_title(self, result):
        """Return the title of a result."""
        return six.text_type(result)


class WorkgroupAutocomplete(GenericAutocomplete):
    model = models.Workgroup
    template_name = "aristotle_mdr/actions/autocompleteWorkgroup.html"

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        if self.q:
            qs = self.request.user.profile.editable_workgroups.filter(
                Q(definition__icontains=self.q) |
                Q(name__icontains=self.q)
            )
        else:
            qs = self.request.user.profile.editable_workgroups

        qs = qs.order_by('name')
        return qs

    def get_result_text(self, result):
        """Return the label of a result."""

        template = get_template(self.template_name)
        context = {"choice": result, 'request': self.request}
        return template.render(context)
