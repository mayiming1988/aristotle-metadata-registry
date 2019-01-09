from datetime import timedelta
from django.conf import settings
from django.utils.timezone import now
from haystack.views import FacetedSearchView


class PermissionSearchView(FacetedSearchView):

    results_per_page_values = getattr(settings, 'RESULTS_PER_PAGE', [])

    def build_page(self):

        try:
            rpp = self.form.cleaned_data['rpp']
        except (AttributeError, KeyError):
            rpp = ''

        if rpp in self.results_per_page_values:
            self.results_per_page = rpp
        else:
            if len(self.results_per_page_values) > 0:
                self.results_per_page = self.results_per_page_values[0]

        return super().build_page()

    def build_form(self):

        form = super().build_form()
        form.request = self.request
        form.request.GET = self.clean_facets(self.request)
        return form

    def clean_facets(self, request):
        get = request.GET.copy()
        for k, val in get.items():
            if k.startswith('f__'):
                get.pop(k)
                k = k[4:]
                get.update({'f': '%s::%s' % (k, val)})
        return get

    def extra_context(self):
        # needed to compare to indexed primary key value
        recently_viewed = {}
        favourites_list = []
        last_month = now() - timedelta(days=31)
        if not self.request.user.is_anonymous():
            from django.db.models import Count, Max
            favourites_list = self.request.user.profile.favourite_item_pks
            recently_viewed = dict(
                (
                    row["concept"],
                    {
                        "count": row["count_viewed"],
                        "last_viewed": row["last_viewed"]
                    }
                )
                for row in self.request.user.recently_viewed_metadata.all().filter(
                    view_date__gt=last_month
                ).values(
                    "concept"
                ).annotate(
                    count_viewed=Count('concept'),
                    last_viewed=Max("view_date")
                )
            )

        return {
            'rpp_values': self.results_per_page_values,
            'favourites': favourites_list,
            'recently_viewed': recently_viewed,
        }
