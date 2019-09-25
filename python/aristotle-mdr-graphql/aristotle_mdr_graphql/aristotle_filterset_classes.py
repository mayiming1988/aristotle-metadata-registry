from django_filters.filterset import FilterSet
import django_filters
from aristotle_mdr.models import _concept


class AristotleIdFilterSet(FilterSet):
    aristotle_id = django_filters.CharFilter(field_name='id')


class IdentifierFilterSet(FilterSet):
    namespace = django_filters.CharFilter(field_name='namespace__shorthand_prefix', lookup_expr='iexact', distinct=True)

    class Meta:
        fields = ['namespace']


class StatusFilterSet(FilterSet):
    is_current = django_filters.BooleanFilter(method='filter_is_current')
    ra = django_filters.CharFilter(field_name='registrationAuthority__uuid', lookup_expr='iexact', distinct=True)

    class Meta:
        fields = ['is_current', 'ra']

    def filter_is_current(self, qs, name, value):
        if name == "is_current" and value:
            return qs.current()
        else:
            return qs


class ConceptFilterSet(FilterSet):
    class Meta:
        model = _concept
        fields = {
            'name': ['exact', 'icontains', 'iexact'],
            'uuid': ['exact'],
        }
    aristotle_id = django_filters.CharFilter(field_name='id')
    identifier = django_filters.CharFilter(field_name='identifiers__identifier', lookup_expr='iexact', distinct=True)
    identifier_namespace = django_filters.CharFilter(field_name='identifiers__namespace__shorthand_prefix', lookup_expr='iexact', distinct=True)
    identifier_version = django_filters.CharFilter(field_name='identifiers__version', lookup_expr='iexact', distinct=True)
    only_public = django_filters.BooleanFilter(method='filter_only_public')

    def filter_only_public(self, qs, name, value):
        if name == "only_public" and value:
            return qs.public()
        else:
            return qs


class CollectionFilterSet(AristotleIdFilterSet):
    only_public = django_filters.BooleanFilter(method='filter_only_public')

    def filter_only_public(self, qs, name, value):
        if name == "only_public" and value:
            return qs.public()
        else:
            return qs
