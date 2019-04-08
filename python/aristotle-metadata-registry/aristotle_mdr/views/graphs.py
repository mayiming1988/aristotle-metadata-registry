from django.views.generic import TemplateView
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import SimpleItemGet
from aristotle_mdr.utils import is_active_extension


class ItemGraphView(TemplateView, SimpleItemGet):
    model = MDR._concept
    template_name = "aristotle_mdr/graphs/item_graphs.html"
    pk_url_kwarg = 'iid'

    def get(self, request, *args, **kwargs):
        item = self.get_item(request.user)
        self.item = item
        return super(ItemGraphView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'graphs'
        context['hide_item_actions'] = True
        context['item'] = self.item.item
        context['links_active'] = is_active_extension('aristotle_mdr_links')
        return context
