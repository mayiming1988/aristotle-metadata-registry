from typing import List
from django.views.generic import ListView


class BootTableListView(ListView):
    template_name='aristotle_mdr/generic/boottablelist.html'
    headers: List[str]
    attrs: List[str]
    page_heading='List'

    def get_context_data(self):
        context = super().get_context_data()
        context['headers'] = self.headers
        if context['page_obj'] is not None:
            iterable = context['page_obj']
        else:
            iterable = context['object_list']

        final_list = []
        for item in iterable:
            item_attrs = []
            for attr in self.attrs:
                item_attrs.append(getattr(item, attr))
            final_list.append(item_attrs)

        context['list'] = final_list
        return context
