from dal.autocomplete import ModelSelect2Multiple, ModelSelect2
from django.db.models import Model
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
    model: Model = None
    # Url name of view to fetch options from
    url_name: str = None
    type: str = 'single'  # choices are 'single' and 'multi'
    item_url_name: str = 'aristotle:item'

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", None)
        url = self.get_url()

        css_class = 'aristotle-select2'
        if self.type == 'multiple':
            css_class += '-multiple'

        kwargs.update(
            url=url,
            attrs={
                'class': css_class,
                'data-html': 'true',
            }
        )
        super().__init__(*args, **kwargs)

    def get_url(self):
        """Get url for select2 to query"""
        return get_django_url(self.url_name, self.model)

    def get_item_url(self, identifier):
        """Get url for single item"""
        return reverse(self.item_url_name, args=[identifier])

    def create_option(self, *args, **kwargs):
        """Set data-item-url on option"""
        option = super().create_option(*args, **kwargs)
        value = option['value']
        if value and self.item_url_name:
            option['attrs']['data-item-url'] = self.get_item_url(value)
        return option


class ConceptAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url_name = 'aristotle-autocomplete:concept'
    type = 'multiple'


class ConceptAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url_name = 'aristotle-autocomplete:concept'


class RelationAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url_name = 'aristotle-autocomplete:relation'


class UserAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url_name = 'aristotle-autocomplete:user'


class UserAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url_name = 'aristotle-autocomplete:user'
    type = 'multiple'


class FrameworkDimensionAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url_name = 'aristotle-autocomplete:framework'


class FrameworkDimensionAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url_name = 'aristotle-autocomplete:framework'
    type = 'multiple'


class WorkgroupAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url_name = 'aristotle-autocomplete:workgroup'
    item_url_name = 'aristotle:workgroup'


class CollectionSelect(AristotleSelect2Mixin, ModelSelect2):
    url_name = 'aristotle-autocomplete:collection'
    item_url_name = 'aristotle:stewards:group:collection_detail_view'

    def __init__(self, *args, **kwargs):
        self.so_slug = kwargs.pop('steward_organisation_slug', None)
        self.so_uuid = kwargs.pop('steward_organisation_uuid', None)
        self.current_collection_id = kwargs.pop('current_collection_id', None)
        super().__init__(*args, **kwargs)

    def get_url(self):
        url = reverse(self.url_name, args=[str(self.so_uuid)])

        if self.current_collection_id is not None:
            url += '?exclude={}'.format(self.current_collection_id)

        return url

    def get_item_url(self, identifier):
        return reverse(self.item_url_name, args=[self.so_slug, identifier])

    def get_initial_item_url(self):
        return '/steward/' + self.so_slug + '/collection/{id}'
