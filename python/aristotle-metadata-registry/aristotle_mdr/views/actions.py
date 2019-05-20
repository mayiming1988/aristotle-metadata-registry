from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView

from braces.views import PermissionRequiredMixin

from aristotle_mdr import perms
from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.generic.views import UnorderedGenericAlterOneToManyView
from aristotle_mdr.forms import actions
from aristotle_mdr.views.utils import (
    generate_visibility_matrix,
    ObjectLevelPermissionRequiredMixin,
    UserFormViewMixin
)
from aristotle_mdr.utils import url_slugify_concept

import logging
logger = logging.getLogger(__name__)


class ItemSubpageView(object):
    def get_item(self):
        self.item = get_object_or_404(MDR._concept, pk=self.kwargs['iid']).item
        if not self.item.can_view(self.request.user):
            raise PermissionDenied
        return self.item

    def dispatch(self, request, *args, **kwargs):
        self.item = self.get_item()
        return super().dispatch(request, *args, **kwargs)


class ItemSubpageFormView(ItemSubpageView, FormView):
    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(*args, **kwargs)
        kwargs['item'] = self.get_item()
        return kwargs


class CheckCascadedStates(ItemSubpageView, DetailView):
    pk_url_kwarg = 'iid'
    context_object_name = 'item'
    queryset = MDR._concept.objects.all()
    template_name = 'aristotle_mdr/actions/check_states.html'

    def dispatch(self, *args, **kwargs):
        self.item = self.get_item()
        if not self.item.item.registry_cascade_items:
            raise Http404
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(*args, **kwargs)

        state_matrix = [
            # (item,[(states_ordered_alphabetically_by_ra_as_per_parent_item,state_of_parent_with_same_ra)],[extra statuses] )
            ]
        item = self.get_item()
        states = []
        ras = []
        for s in item.current_statuses():
            if s.registrationAuthority not in ras:
                ras.append(s.registrationAuthority)
                states.append(s)

        for i in item.item.registry_cascade_items:
            sub_states = [(None, None)] * len(ras)
            extras = []
            for s in i.current_statuses():
                ra = s.registrationAuthority
                if ra in ras:
                    sub_states[ras.index(ra)] = (s, states[ras.index(ra)])
                else:
                    extras.append(s)
            state_matrix.append((i, sub_states, extras))

        kwargs['known_states'] = states
        kwargs['state_matrix'] = state_matrix
        return kwargs


class DeleteSandboxView(UserFormViewMixin, FormView):

    form_class = actions.DeleteSandboxForm
    template_name = "aristotle_mdr/actions/delete_sandbox.html"

    def get_success_url(self):
        return reverse('aristotle:userSandbox')

    def get_initial(self):
        initial = super().get_initial()
        item = self.request.GET.get('item', None)
        if item:
            initial.update({'item': item})

        return initial

    def form_invalid(self, form):

        if self.request.is_ajax():
            if 'item' in form.errors:
                return JsonResponse({'completed': False, 'message': form.errors['item']})
            else:
                return JsonResponse({'completed': False, 'message': 'Invalid data'})

        return super().form_invalid(form)

    def form_valid(self, form):

        item = form.cleaned_data['item']
        item.delete()

        if self.request.is_ajax():
            return JsonResponse({'completed': True})

        return super().form_valid(form)


class SupersedeItemView(UnorderedGenericAlterOneToManyView, ItemSubpageView, PermissionRequiredMixin):
    permission_checks = [perms.user_can_supersede]
    model_base = MDR._concept
    model_to_add = MDR.SupersedeRelationship
    model_base_field = 'superseded_by_items_relation_set'
    model_to_add_field = 'older_item'
    form_add_another_text = _('Add a relationship')
    form_title = _('Change Superseding')

    def has_permission(self):
        return perms.user_can_supersede(self.request.user, self.item)

    def get_success_url(self):
        return url_slugify_concept(self.item)

    def get_editable_queryset(self):
        if self.request.user.is_superuser:
            return super().get_editable_queryset()
        return super().get_editable_queryset().filter(
            registration_authority__registrars__profile__user=self.request.user
        )

    def get_form(self):
        return actions.SupersedeForm

    def get_form_kwargs(self):
        return {
            "item": self.item.item,
            "user": self.request.user,
        }


class ProposedSupersedeItemView(SupersedeItemView):
    permission_checks = [perms.user_can_supersede]
    form_add_another_text = _('Add a proposed relationship')
