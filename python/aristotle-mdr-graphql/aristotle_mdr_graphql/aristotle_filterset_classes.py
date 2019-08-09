from django_filters.filterset import FilterSet
import django_filters


class AristotleIdFilterSet(FilterSet):
    aristotle_id = django_filters.CharFilter(name='id')


class IdentifierFilterSet(FilterSet):
    namespace = django_filters.CharFilter(name='namespace__shorthand_prefix', lookup_expr='iexact', distinct=True)

    class Meta:
        fields = ['namespace']


class StatusFilterSet(FilterSet):
    is_current = django_filters.BooleanFilter(method='filter_is_current')
    ra = django_filters.CharFilter(name='registrationAuthority__uuid', lookup_expr='iexact', distinct=True)

    class Meta:
        fields = ['is_current', 'ra']

    def filter_is_current(self, qs, name, value):
        if name == "is_current" and value:
            return qs.current()
        else:
            return qs


class ConceptFilterSet(FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr=['exact', 'icontains', 'iexact'])
    uuid = django_filters.CharFilter(name='uuid', lookup_expr='exact', distinct=True)
    aristotle_id = django_filters.CharFilter(name='id')
    identifier = django_filters.CharFilter(name='identifiers__identifier', lookup_expr='iexact', distinct=True)
    identifier_namespace = django_filters.CharFilter(name='identifiers__namespace__shorthand_prefix', lookup_expr='iexact', distinct=True)
    identifier_version = django_filters.CharFilter(name='identifiers__version', lookup_expr='iexact', distinct=True)
    only_public = django_filters.BooleanFilter(method='filter_only_public')

    def filter_only_public(self, qs, name, value):
        if name == "only_public" and value:
            return qs.public()
        else:
            return qs


class CollectionFilterSet(FilterSet):
    only_public = django_filters.BooleanFilter(method='filter_only_public')

    def filter_only_public(self, qs, name, value):
        if name == "only_public" and value:
            return qs.public()
        else:
            return qs