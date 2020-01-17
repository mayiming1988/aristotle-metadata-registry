from dal.autocomplete import ModelSelect2Multiple, ModelSelect2
from django.urls import reverse_lazy, reverse


def get_django_url(url: str, model=None) -> str:
    if url and model:
        url = reverse_lazy(
            url,
            args=[model._meta.app_label, model._meta.model_name]
        )
    elif url:
        url = reverse_lazy(url)
    else:
        raise ValueError("get_django_url requires a django URL name as parameter")
    return url


class AristotleSelect2Mixin:
    url: str = None
    type: str = 'single'  # choices are 'single' and 'multi'

    def __init__(self, *args, **kwargs):
        url = self.get_url(kwargs)

        css_class = 'aristotle-select2'
        if self.type == 'multiple':
            css_class += '-multiple'

        kwargs.update(
            url=url,
            attrs={
                'class': css_class,
                'data-html': 'true'
            }
        )
        super().__init__(*args, **kwargs)

    def get_url(self, kwargs):
        """Get url for select2 to query
        If using args passed to widget pop them off here"""
        model = kwargs.pop("model", None)
        return get_django_url(self.url, model)


class ConceptAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url = 'aristotle-autocomplete:concept'
    type = 'multiple'


class ConceptAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:concept'


class RelationAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:relation'


class UserAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:user'


class UserAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url = 'aristotle-autocomplete:user'
    type = 'multiple'


class FrameworkDimensionAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:framework'


class FrameworkDimensionAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url = 'aristotle-autocomplete:framework'
    type = 'multiple'


class WorkgroupAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:workgroup'


class CollectionSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:collection'

    def get_url(self, kwargs):
        so_uuid = kwargs.pop('steward_organisation_uuid')

        url = reverse(self.url, args=[str(so_uuid)])

        if 'current_collection_id' in kwargs:
            current_collection_id = kwargs.pop('current_collection_id')
            url += '?exclude={}'.format(current_collection_id)

        return url
