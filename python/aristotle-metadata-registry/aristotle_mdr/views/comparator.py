from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from reversion.models import Version
from reversion.errors import RevertError

from aristotle_mdr.forms import CompareConceptsForm
from aristotle_mdr.models import _concept

import logging
logger = logging.getLogger(__name__)


class CompareConceptsView(TemplateView):
    template_name = 'aristotle_mdr/actions/compare/compare_items.html'

    def get_form(self, data, user):
        qs = _concept.objects.visible(user)
        return CompareConceptsForm(data, user=user, qs=qs)  # A form bound to the POST data

    def get(self, request, *args, **kwargs):
        comparison = {}

        form = self.get_form(request.GET, request.user)
        context = {'form': form, 'failed': False}

        if form.is_valid():
            # Get items from form
            item_a = form.cleaned_data['item_a'].item
            item_b = form.cleaned_data['item_b'].item
            context.update({'item_a': item_a, 'item_b': item_b})

            revs=[]
            for item in [item_a, item_b]:
                version = Version.objects.get_for_object(item).order_by('-revision__date_created').first()
                revs.append(version)
            if revs[0] is None:
                form.add_error('item_a', _('This item has no revisions. A comparison cannot be made'))
            if revs[1] is None:
                form.add_error('item_b', _('This item has no revisions. A comparison cannot be made'))
            if revs[0] is not None and revs[1] is not None:
                comparator_a_to_b = item_a.comparator()
                comparator_b_to_a = item_b.comparator()

                version1 = revs[0]
                version2 = revs[1]

                try:
                    compare_data_a, has_unfollowed_fields_a = comparator_a_to_b.compare(item_a, version2, version1)
                    compare_data_b, has_unfollowed_fields_b = comparator_b_to_a.compare(item_a, version1, version2)
                except RevertError:
                    # Catch deserialization error
                    context['failed'] = True
                    kwargs.update(context)
                    return super().get(request, *args, **kwargs)

                context.update({'debug': {'cmp_a': compare_data_a}})
                comparison = {}
                for field_diff_a in compare_data_a:
                    name = field_diff_a['field'].name
                    x = comparison.get(name, {})
                    x['field'] = field_diff_a['field']
                    x['a'] = field_diff_a['diff']
                    comparison[name] = x
                for field_diff_b in compare_data_b:
                    name = field_diff_b['field'].name
                    comparison.get(name, {})['b'] = field_diff_b['diff']

                same = {}
                for f in item_a._meta.fields:
                    if f.name not in comparison.keys():
                        same[f.name] = {'field': f, 'value': getattr(item_a, f.name)}
                    if f.name.startswith('_'):
                        # hidden field
                        comparison.pop(f.name, None)
                        same.pop(f.name, None)

                hidden_fields = ['workgroup', 'created', 'modified', 'id', 'submitter', 'statuses', 'uuid']
                for h in hidden_fields:
                    comparison.pop(h, None)
                    same.pop(h, None)

                only_a = {}
                for f in item_a._meta.fields:
                    if (f not in item_b._meta.fields and f not in comparison.keys() and f not in same.keys() and f.name not in hidden_fields):
                        only_a[f.name] = {'field': f, 'value': getattr(item_a, f.name)}

                only_b = {}
                for f in item_b._meta.fields:
                    if (f not in item_a._meta.fields and f not in comparison.keys() and f not in same.keys() and f.name not in hidden_fields):
                        only_b[f.name] = {'field': f, 'value': getattr(item_b, f.name)}

                comparison = sorted(comparison.items())
                context.update({
                    "comparison": comparison,
                    "same": same,
                    "only_a": only_a,
                    "only_b": only_b,
                })

        kwargs.update(context)
        return super().get(request, *args, **kwargs)
