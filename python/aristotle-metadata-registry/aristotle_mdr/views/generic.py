from typing import List
from copy import copy
from django.urls import reverse
from django.views.generic import ListView, DeleteView


class BootTableListView(ListView):
    """Lists objects in a bootstrap table (with optional pagination)"""
    template_name='aristotle_mdr/generic/boottablelist.html'
    # Need to override these
    headers: List[str]
    attrs: List[str]
    model_name=''
    # Can optionally override these
    page_heading=''
    create_button_text=''
    create_url_name=''
    delete_url_name=''
    update_url_name=''

    def get_context_data(self):
        context = super().get_context_data()
        headers = copy(self.headers)
        if self.page_heading:
            page_heading = self.page_heading
        else:
            page_heading = 'List of {}s'.format(self.model_name)

        if self.create_button_text:
            create_button_text = self.create_button_text
        else:
            create_button_text = 'New {}'.format(self.model_name)

        if self.update_url_name:
            headers.append('Update')
        if self.delete_url_name:
            headers.append('Delete')

        if context['page_obj'] is not None:
            iterable = context['page_obj']
        else:
            iterable = context['object_list']

        final_list = []
        for item in iterable:
            itemdict = {'attrs': [], 'pk': item.pk}
            for attr in self.attrs:
                itemdict['attrs'].append(getattr(item, attr))
            final_list.append(itemdict)

        context.update({
            'list': final_list,
            'headers': headers,
            'page_heading': page_heading,
            'create_button_text': create_button_text,
            'create_url': reverse(self.create_url_name),
            'delete_url_name': self.delete_url_name,
            'update_url_name': self.update_url_name
        })
        return context


class DeleteCancelView(DeleteView):
    pass
