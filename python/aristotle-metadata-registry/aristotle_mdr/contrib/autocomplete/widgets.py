from dal.autocomplete import ModelSelect2Multiple, ModelSelect2
from django.urls import reverse_lazy


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
    model = None
    type: str = 'single'  # choices are 'single' and 'multi'

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        url = get_django_url(self.url, model)
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
