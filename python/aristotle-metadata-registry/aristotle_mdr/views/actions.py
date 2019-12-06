from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView, UpdateView, CreateView, TemplateView
from django.db import transaction

from aristotle_mdr import perms, perms_utils
from aristotle_mdr import models as MDR
from aristotle_mdr.forms import actions
from aristotle_mdr.views.utils import UserFormViewMixin
from aristotle_mdr.models import SupersedeRelationship
from aristotle_mdr.contrib.generic.views import ConfirmDeleteView
from aristotle_mdr.structs import Breadcrumb


import logging
logger = logging.getLogger(__name__)


class CheckCascadedStates(DetailView):
    pk_url_kwarg = 'iid'
    context_object_name = 'item'
    queryset = MDR._concept.objects.all()
    template_name = 'aristotle_mdr/actions/check_states.html'

    def dispatch(self, *args, **kwargs):
        self.item = self.get_item()
        if not self.item.item.registry_cascade_items:
            raise Http404
        return super().dispatch(*args, **kwargs)

    def get_item(self):
        self.item = get_object_or_404(MDR._concept, pk=self.kwargs['iid']).item
        if not self.item.can_view(self.request.user):
            raise PermissionDenied
        return self.item

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

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
    template_name = "aristotle_mdr/actions/delete_sandbox.html"
    form_class = actions.DeleteSandboxForm

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

    @transaction.atomic()
    def form_valid(self, form):
        # This probably shouldn't be a transaction, but haystack in its infinite wisdom
        # requires you pass an instance to delete the search index.

        item = form.cleaned_data['item']
        item.delete()

        if self.request.is_ajax():
            return JsonResponse({'completed': True})

        return super().form_valid(form)


class SupersedeItemHistoryBase(LoginRequiredMixin, TemplateView):
    template_name = "aristotle_mdr/supersede_item_history.html"
    only_proposed = False
    item = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.only_proposed:
            supersedes = SupersedeRelationship.objects.filter(newer_item=self.item, proposed=True).order_by("registration_authority")
            context.update({
                'proposed': True
            })
        else:
            supersedes = SupersedeRelationship.objects.filter(newer_item=self.item).order_by("registration_authority")

        out = {}

        for sup in supersedes:
            if sup.registration_authority in out.keys():
                out[sup.registration_authority].append(sup)
            else:
                out[sup.registration_authority] = [sup]

        context.update({
            'item': self.item,
            'history': out,
        })

        return context


class SupersedeItemHistory(SupersedeItemHistoryBase):
    """
    The purpose of this view is to list all the SupersedeRelationship objects related to a superseded item.
    """

    def dispatch(self, request, *args, **kwargs):
        self.item = perms_utils.get_if_user_can_supersede(MDR._concept, request.user, self.kwargs.get('iid'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.name,
                    'aristotle:item',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Supersede relationships",
                    active=True
                ),
            ]
        })
        return context


class ProposedSupersedeItemHistory(SupersedeItemHistoryBase):
    """
    The purpose of this view is to list all the "proposed" SupersedeRelationship objects related to a superseded item.
    """
    only_proposed = True

    def dispatch(self, request, *args, **kwargs):
        self.item = perms_utils.get_if_user_can_edit(MDR._concept, request.user, self.kwargs.get('iid'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.name,
                    'aristotle:item',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Proposed supersede relationships",
                    active=True
                ),
            ],
        })
        return context


class SupersedeRelationshipCreateView(LoginRequiredMixin, CreateView):
    model = MDR.SupersedeRelationship
    template_name = "aristotle_mdr/add_supersede_items.html"
    pk_url_kwarg = 'iid'

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.item = self.get_item()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "item": self.item,
            "user": self.request.user,
        })
        return kwargs

    def get_item(self):
        """Override this method to get the concept related to the SupersedeRelationship object"""
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context

    def form_valid(self, form):
        form.instance.newer_item = self.item
        return super(SupersedeRelationshipCreateView, self).form_valid(form)


class AddSupersedeRelationship(SupersedeRelationshipCreateView):
    """
    The purpose of this view is to create a SupersedeRelationship object for a concept.
    """
    form_class = actions.SupersedeRelationshipFormWithProposed

    def get_item(self):
        return perms_utils.get_if_user_can_supersede(MDR._concept, self.user, self.kwargs['iid']).item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.name,
                    'aristotle:item',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Supersede relationships",
                    'aristotle:supersede',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Add supersede relationship",
                    active=True
                )
            ]
        })
        return context

    def get_success_url(self):
        return reverse("aristotle:supersede", args=[self.item.pk])


class AddProposedSupersedeRelationship(SupersedeRelationshipCreateView):
    """
    The purpose of this view is to create a "proposed" SupersedeRelationship object for a concept.
    """
    form_class = actions.SupersedeRelationshipForm

    def get_item(self):
        return perms_utils.get_if_user_can_edit(MDR._concept, self.user, self.kwargs['iid']).item

    def form_valid(self, form):
        form.instance.proposed = True
        return super(AddProposedSupersedeRelationship, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.name,
                    'aristotle:item',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Proposed supersede relationships",
                    'aristotle:proposed_supersede',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Add proposed supersede relationship",
                    active=True
                )
            ],
            "proposed": True,
        })
        return context

    def get_success_url(self):
        return reverse("aristotle:proposed_supersede", args=[self.item.pk])


class SupersedeRelationshipUpdateView(LoginRequiredMixin, UpdateView):
    model = MDR.SupersedeRelationship
    template_name = "aristotle_mdr/edit_superseded_items.html"
    pk_url_kwarg = "iid"

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.item = self.get_item()
        return super().dispatch(request, *args, **kwargs)

    def get_item(self):
        """
        Override this method to get the concept related to the SupersedeRelationship object, and apply the necessary
        permissions.
        """
        raise NotImplementedError

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "item": self.item,
            "user": self.user,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context


class EditSupersedeRelationship(SupersedeRelationshipUpdateView):
    """
    The purpose of this view is to edit a SupersedeRelationship object.
    """
    form_class = actions.SupersedeRelationshipFormWithProposed

    def get_item(self):
        item = get_object_or_404(self.model, pk=self.kwargs['iid'])
        if perms.user_can_supersede(self.user, item.newer_item):
            return item.newer_item
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.name,
                    'aristotle:item',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Supersede relationships",
                    'aristotle:supersede',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Edit supersede relationship",
                    active=True
                )
            ]
        })
        return context

    def get_success_url(self):
        return reverse("aristotle:supersede", args=[self.item.pk])


class EditProposedSupersedeRelationship(SupersedeRelationshipUpdateView):
    """
    The purpose of this view is to edit a "proposed" SupersedeRelationship object.
    """
    form_class = actions.SupersedeRelationshipForm

    def get_item(self):
        item = get_object_or_404(self.model, pk=self.kwargs['iid'])
        if perms.user_can_edit(self.user, item.newer_item):
            return item.newer_item
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.name,
                    'aristotle:item',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Proposed supersede relationships",
                    'aristotle:proposed_supersede',
                    url_args=[self.item.id]
                ),
                Breadcrumb(
                    "Edit proposed supersede relationship",
                    active=True
                ),
            ],
            'proposed': True,
        })
        return context

    def get_success_url(self):
        return reverse("aristotle:proposed_supersede", args=[self.item.pk])


class SupersedeRelationshipConfirmDeleteView(LoginRequiredMixin, ConfirmDeleteView):
    model_base = MDR.SupersedeRelationship
    form_title = "Delete Supersede Relationship"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "item": self.item.newer_item,
        })
        return context

    def post(self, *args, **kwargs):
        return self.perform_deletion()


class DeleteSupersedeRelationship(SupersedeRelationshipConfirmDeleteView):
    """
    The purpose of this view is to delete a SupersedeRelationship object.
    """
    reverse_url = "aristotle:supersede"
    permission_checks = [perms.user_can_supersede]

    def get_warning_text(self):
        return f"You are about to delete the supersede relationship between superseding item `{self.item.newer_item}` and " \
               f"superseded item `{self.item.older_item}` within the registration authority `{self.item.registration_authority}`. Are you sure you want to continue?"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.newer_item.name,
                    'aristotle:item',
                    url_args=[self.item.newer_item.id]
                ),
                Breadcrumb(
                    "Supersede relationships",
                    "aristotle:supersede",
                    url_args=[self.item.newer_item.id]
                ),
                Breadcrumb(
                    "Delete supersede relationship",
                    active=False
                )
            ]
        })
        return context

    def perform_deletion(self):
        self.item.delete()
        return HttpResponseRedirect(reverse('aristotle:supersede', args=[self.item.newer_item.pk]))


class DeleteProposedSupersedeRelationship(SupersedeRelationshipConfirmDeleteView):
    """
    The purpose of this view is to delete a "proposed" SupersedeRelationship object.
    """
    reverse_url = "aristotle:proposed_supersede"
    permission_checks = [perms.user_can_edit]

    def get_warning_text(self):
        return f"You are about to delete the proposed supersede relationship between superseding item `{self.item.newer_item}` and " \
               f"superseded item `{self.item.older_item}` within the registration authority `{self.item.registration_authority}`. Are you sure you want to continue?"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "breadcrumbs": [
                Breadcrumb(
                    self.item.newer_item.name,
                    'aristotle:item',
                    url_args=[self.item.newer_item.id]
                ),
                Breadcrumb(
                    "Proposed supersede relationships",
                    "aristotle:supersede",
                    url_args=[self.item.newer_item.id]
                ),
                Breadcrumb(
                    "Delete proposed supersede relationship",
                    active=False
                )
            ]
        })
        return context

    def perform_deletion(self):
        self.item.delete()
        return HttpResponseRedirect(reverse('aristotle:proposed_supersede', args=[self.item.newer_item.pk]))
