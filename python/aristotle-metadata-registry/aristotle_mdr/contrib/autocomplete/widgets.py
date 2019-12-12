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
    size: str = 'standard'  # choices are 'standard' and 'large'

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        url = get_django_url(self.url, model)
        css_class = 'aristotle-select2'
        if self.size == 'large':
            css_class += '-large'

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
    size = 'large'


class ConceptAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:concept'


class UserAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:user'


class UserAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url = 'aristotle-autocomplete:user'
    size = 'large'


class FrameworkDimensionAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:framework'


class FrameworkDimensionAutocompleteSelectMultiple(AristotleSelect2Mixin, ModelSelect2Multiple):
    url = 'aristotle-autocomplete:framework'
    size = 'large'


class WorkgroupAutocompleteSelect(AristotleSelect2Mixin, ModelSelect2):
    url = 'aristotle-autocomplete:workgroup'
