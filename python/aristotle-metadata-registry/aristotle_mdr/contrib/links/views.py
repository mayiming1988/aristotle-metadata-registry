from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from aristotle_mdr import models as MDR
from aristotle_mdr.perms import user_can_edit
from aristotle_mdr.structs import Breadcrumb
from aristotle_mdr.views.utils import get_item_breadcrumbs

from aristotle_mdr.contrib.links import forms as link_forms
from aristotle_mdr.contrib.links import models as link_models
from aristotle_mdr.contrib.links import perms
from aristotle_mdr.contrib.links.utils import get_links_for_concept
from aristotle_mdr.contrib.generic.views import ConfirmDeleteView

from formtools.wizard.views import SessionWizardView
import logging

logger = logging.getLogger(__name__)


class EditLinkFormView(FormView):
    template_name = "aristotle_mdr_links/actions/edit_link.html"
    form_class = link_forms.LinkEndEditor

    def dispatch(self, request, *args, **kwargs):
        self.link = get_object_or_404(
            link_models.Link, pk=self.kwargs['linkid']
        )
        self.relation = self.link.relation
        if request.user.is_anonymous:
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        if not perms.user_can_change_link(request.user, self.link):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'link': self.link,
            'roles': self.link.relation.relationrole_set.all(),
            'user': self.request.user
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        breadcrumbs = get_item_breadcrumbs(item=self.link.root_item.item, user=self.request.user, last_active=False)
        breadcrumbs.append(Breadcrumb("Edit Link"))

        context.update(
            {
                'roles': self.link.relation.relationrole_set.all(),
                'link': self.link,
                'breadcrumbs': breadcrumbs,
                'relation': self.link.relation,
                'root_item': self.link.root_item
            }
        )
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', None)
        if next_url:
            return next_url
        else:
            return self.link.relation.get_absolute_url()

    @transaction.atomic
    def form_valid(self, form):
        role_concepts = form.cleaned_data
        roles = self.link.relation.relationrole_set.order_by('ordinal', 'name')

        for role in roles:
            concepts = role_concepts['role_' + str(role.pk)]
            try:
                concepts = list(concepts)
            except TypeError:
                concepts = [concepts]
            current_ends = link_models.LinkEnd.objects.filter(
                link=self.link,
                role=role
            )

            # Remove those that are deleted
            for end in current_ends:
                if end.concept_id not in [c.pk for c in concepts]:
                    end.delete()

            # Add those that are new
            for concept in concepts:
                if concept.pk not in [c.concept_id for c in current_ends]:
                    link_models.LinkEnd.objects.create(link=self.link, role=role, concept=concept)

        return HttpResponseRedirect(self.get_success_url())


class AddLinkWizard(SessionWizardView):
    form_list = base_form_list = [
        link_forms.AddLink_SelectRelation_0,
        link_forms.AddLink_SelectConcepts_1,
    ]
    base_form_count = len(form_list)
    template_names = [
        "aristotle_mdr_links/actions/add_link_wizard_0_select_relation.html",
        "aristotle_mdr_links/actions/add_link_wizard_1_select_concepts.html",
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        if not request.user.has_perm('aristotle_mdr_links.add_link'):
            raise PermissionDenied

        self.root_item = get_object_or_404(MDR._concept, id=kwargs['iid'])

        if not user_can_edit(self.request.user, self.root_item):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return self.template_names[int(self.steps.current)]

    def get_roles(self):
        self.relation = self.get_cleaned_data_for_step('0')['relation']
        return self.relation.relationrole_set.order_by('ordinal', 'name')

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        istep = int(step)
        if istep == 0:
            kwargs['user'] = self.request.user
        elif istep == 1:
            relation = self.get_cleaned_data_for_step('0')['relation']
            kwargs.update({
                'roles': relation.relationrole_set.all(),
                'user': self.request.user,
                'root_item': self.root_item
            })

        return kwargs

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        istep = int(step)

        if istep == 1:
            role = self.get_roles()[0]
            rolekey = 'role_{}'.format(role.pk)
            initial[rolekey] = self.root_item

        return initial

    def get_role_concepts(self):
        role_concepts = []
        for role, concepts in zip(self.get_roles(), self.get_cleaned_data_for_step('1').values()):
            if role.multiplicity == 1:
                concepts = [concepts]
            role_concepts.append((role, concepts))
        return role_concepts

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        istep = int(self.steps.current)

        # For steps after 1 pass relation
        if istep > 0:
            context['relation'] = self.get_cleaned_data_for_step('0')['relation']

        if istep == 1:
            context['roles'] = self.get_roles()

        context['root_item'] = self.root_item
        return context

    @transaction.atomic
    def done(self, *args, **kwargs):
        self.relation = self.get_cleaned_data_for_step('0')['relation']

        link = link_models.Link.objects.create(
            relation=self.relation,
            root_item=self.root_item
        )
        for role, concepts in self.get_role_concepts():
            for concept in concepts:
                link_models.LinkEnd.objects.create(link=link, role=role, concept=concept)

        return HttpResponseRedirect(
            reverse('aristotle:item', args=[self.root_item.id])
        )


def link_json_for_item(request, iid):
    item = get_object_or_404(MDR._concept, pk=iid).item
    links = get_links_for_concept(item)

    nodes = []
    edges = []
    for link in links:
        for end in link.linkend_set.all():
            if 'concept_%s' % end.concept.id not in [i['id'] for i in nodes]:
                if end.concept == item.concept:
                    nodes.append({
                        'id': 'concept_%s' % end.concept.id,
                        'label': end.concept.name,
                        'group': 'active',
                        'title': "<i>This item</i>",
                    })
                else:
                    nodes.append({
                        'id': 'concept_%s' % end.concept.id,
                        'label': end.concept.name,
                        'group': 'regular',
                        'title': '<a href="%s">%s</a>' % (end.concept.get_absolute_url(), end.concept.name),
                    })
            if end.concept == item.concept:
                edges.append({
                    'to': 'link_%s_%s' % (link.relation.id, link.id),
                    'from': 'concept_%s' % end.concept.id,
                    # 'label': end.role.name
                })
            else:
                edges.append({
                    'from': 'link_%s_%s' % (link.relation.id, link.id),
                    'to': 'concept_%s' % end.concept.id,
                    # 'label': end.role.name
                    'title': end.role.name
                })
        if 'link_%s_%s' % (link.relation.id, link.id) not in [i['id'] for i in nodes]:
            nodes.append({
                'id': 'link_%s_%s' % (link.relation.id, link.id),
                'label': link.relation.name,
                'group': 'relation',
                'title': '<a href="%s">%s</a>' % (link.relation.get_absolute_url(), link.relation.definition),
            })

    return JsonResponse({
        'nodes': nodes,
        'edges': edges,
    })


class RemoveLinkView(ConfirmDeleteView):
    confirm_template = "aristotle_mdr_links/actions/confirm_delete.html"
    template_name = "aristotle_mdr_links/actions/confirm_delete.html"
    model_base = link_models.Link
    form_title = "Delete link"
    form_delete_button_text = _("Delete link")
    permission_checks = [perms.user_can_change_link]
    item_kwarg = 'linkid'

    def dispatch(self, request, *args, **kwargs):
        self.link = get_object_or_404(
            link_models.Link, pk=self.kwargs['linkid']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_warning_text(self):
        return f"You are about to delete the link between {self.item.get_readable_concepts()}. Are you sure" \
               f" you want to continue?"

    def perform_deletion(self):
        self.item.delete()
        return HttpResponseRedirect(reverse('aristotle:item', args=[self.kwargs['iid']]))

    def post(self, *args, **kwargs):
        return self.perform_deletion()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        breadcrumbs = get_item_breadcrumbs(item=self.link.root_item.item, user=self.request.user, last_active=False)
        breadcrumbs.append(Breadcrumb("Edit Link"))

        context.update(
            {
                'links': [self.link],
                'breadcrumbs': breadcrumbs
            }
        )
        return context
