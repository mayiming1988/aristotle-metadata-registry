from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.forms import Select
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied
from django.forms.models import modelform_factory
from django.http.request import QueryDict

import django_filters
from django_filters.views import FilterView

from aristotle_mdr import models as MDR
from aristotle_mdr.forms import actions
from aristotle_mdr.forms.registrationauthority import CreateRegistrationAuthorityForm
from aristotle_mdr.views.utils import (
    paginated_registration_authority_list,
    ObjectLevelPermissionRequiredMixin,
    RoleChangeView,
    MemberRemoveFromGroupView,
    AlertFieldsMixin,
    UserFormViewMixin

)
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from aristotle_mdr import perms
from aristotle_mdr.utils import fetch_aristotle_downloaders

from aristotle_mdr.contrib.validators.views import ValidationRuleEditView
from aristotle_mdr.contrib.validators.models import RAValidationRules

from ckeditor.widgets import CKEditorWidget

import datetime

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class MainPageMixin:
    """Mixin for views displaying on the main (public) ra page"""
    active_tab: str = 'home'

    def is_manager(self, ra):
        return perms.user_can_edit(self.request.user, ra)

    def get_tab_context(self):
        return {
            'active_tab': self.active_tab
        }


class RegistrationAuthorityView(MainPageMixin, DetailView):
    pk_url_kwarg = 'iid'
    queryset = MDR.RegistrationAuthority.objects.all()
    template_name = 'aristotle_mdr/organization/registration_authority/home.html'
    context_object_name = 'item'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_tab_context())
        context['is_manager'] = self.is_manager(self.object)
        return context


def organization(request, iid, *args, **kwargs):
    if iid is None:
        return redirect(reverse("aristotle_mdr:all_organizations"))
    item = get_object_or_404(MDR.Organization, pk=iid).item

    return render(request, item.template, {'item': item.item})


def all_registration_authorities(request):
    # All visible ras
    ras = MDR.RegistrationAuthority.objects.filter(active__in=[0, 1]).order_by('name')
    return render(request, "aristotle_mdr/organization/all_registration_authorities.html", {'registrationAuthorities': ras})


def all_organizations(request):
    orgs = MDR.Organization.objects.order_by('name')
    return render(request, "aristotle_mdr/organization/all_organizations.html", {'organization': orgs})


class CreateRegistrationAuthority(UserFormViewMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = "aristotle_mdr/user/registration_authority/add.html"
    # fields = ['name', 'definition', 'stewardship_organisation']
    permission_required = "aristotle_mdr.add_registration_authority"
    raise_exception = True
    redirect_unauthenticated_users = True
    model = MDR.RegistrationAuthority
    form_class = CreateRegistrationAuthorityForm

    def get_success_url(self):
        return reverse('aristotle:registrationAuthority', kwargs={'iid': self.object.id})


class AddUser(LoginRequiredMixin, ObjectLevelPermissionRequiredMixin, UpdateView):
    template_name = "aristotle_mdr/user/registration_authority/add_user.html"
    permission_required = "aristotle_mdr.change_registrationauthority_memberships"
    raise_exception = True
    redirect_unauthenticated_users = True
    form_class = actions.AddRegistrationUserForm

    model = MDR.RegistrationAuthority
    pk_url_kwarg = 'iid'
    context_object_name = "item"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})

        # TODO: Not happy about this as its not an updateForm
        kwargs.pop('instance')
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(MDR.RegistrationAuthority, pk=self.kwargs.get('iid'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        kwargs = super().get_context_data(**kwargs)
        kwargs.update({'item': self.item})
        return kwargs

    def form_valid(self, form):
        user = form.cleaned_data['user']
        for role in form.cleaned_data['roles']:
            self.item.giveRoleToUser(role, user)

        return redirect(reverse('aristotle:registrationauthority_members', args=[self.item.id]))


class ListRegistrationAuthorityBase(ListView):
    model = MDR.RegistrationAuthority

    def get_queryset(self):
        return super().get_queryset().filter(active__in=[0, 1])

    def render_to_response(self, context, **response_kwargs):
        ras = self.get_queryset()

        text_filter = self.request.GET.get('filter', "")
        if text_filter:
            ras = ras.filter(Q(name__icontains=text_filter) | Q(definition__icontains=text_filter))
        context = self.get_context_data()
        context.update({'filter': text_filter})
        return paginated_registration_authority_list(self.request, ras, self.template_name, context)


class ListRegistrationAuthorityAll(LoginRequiredMixin, PermissionRequiredMixin, ListRegistrationAuthorityBase):
    template_name = "aristotle_mdr/user/registration_authority/list_all.html"
    permission_required = "aristotle_mdr.is_registry_administrator"
    raise_exception = True
    redirect_unauthenticated_users = True


class MembersRegistrationAuthority(LoginRequiredMixin, PermissionRequiredMixin, MainPageMixin, DetailView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/organization/registration_authority/members.html"
    permission_required = "aristotle_mdr.view_registrationauthority_details"
    raise_exception = True
    redirect_unauthenticated_users = True

    pk_url_kwarg = 'iid'
    context_object_name = "item"

    active_tab = 'members'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_tab_context())
        context['is_manager'] = self.is_manager(self.object)
        return context


class EditRegistrationAuthority(LoginRequiredMixin, ObjectLevelPermissionRequiredMixin, AlertFieldsMixin, MainPageMixin, UpdateView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/edit.html"
    permission_required = "aristotle_mdr.change_registrationauthority"
    raise_exception = True
    redirect_unauthenticated_users = True
    object_level_permissions = True

    fields = ('name', 'definition', 'active')
    widgets = {
        'definition': CKEditorWidget
    }

    alert_fields = [
        'active'
    ]

    pk_url_kwarg = 'iid'
    context_object_name = "item"

    active_tab = 'settings'

    def get_form_class(self):
        return modelform_factory(self.model, fields=self.fields, widgets=self.widgets)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_tab_context())
        context['is_manager'] = self.is_manager(self.object)
        context['settings_tab'] = 'general'
        return context


class EditRegistrationAuthorityStates(LoginRequiredMixin, ObjectLevelPermissionRequiredMixin, MainPageMixin, UpdateView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/edit_states.html"
    permission_required = "aristotle_mdr.change_registrationauthority"
    raise_exception = True
    redirect_unauthenticated_users = True
    object_level_permissions = True

    fields = [
        'locked_state',
        'public_state',
        'notprogressed',
        'incomplete',
        'candidate',
        'recorded',
        'qualified',
        'standard',
        'preferred',
        'superseded',
        'retired',
    ]

    pk_url_kwarg = 'iid'
    context_object_name = "item"

    active_tab = 'settings'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_tab_context())
        context['is_manager'] = self.is_manager(self.object)
        context['settings_tab'] = 'states'
        return context


class ChangeUserRoles(RoleChangeView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/change_role.html"
    permission_required = "aristotle_mdr.change_registrationauthority_memberships"
    form_class = actions.ChangeRegistrationUserRolesForm
    pk_url_kwarg = 'iid'
    context_object_name = "item"

    def get_success_url(self):
        return redirect(reverse('aristotle:registrationauthority_members', args=[self.get_object().id]))


class RemoveUser(MemberRemoveFromGroupView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/remove_member.html"
    permission_required = "aristotle_mdr.change_registrationauthority_memberships"
    pk_url_kwarg = 'iid'
    context_object_name = "item"

    def get_success_url(self):
        return redirect(reverse('aristotle:registrationauthority_members', args=[self.get_object().id]))


class RAValidationRuleEditView(SingleObjectMixin, MainPageMixin, ValidationRuleEditView):
    template_name = 'aristotle_mdr/organization/registration_authority/rules.html'
    model = MDR.RegistrationAuthority
    pk_url_kwarg = 'iid'
    context_object_name = 'item'

    active_tab = 'settings'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not perms.user_can_edit(self.request.user, obj):
            raise PermissionDenied

        return obj

    def get_rules(self):
        try:
            rules = RAValidationRules.objects.get(registration_authority=self.object)
        except RAValidationRules.DoesNotExist:
            return None
        return rules

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_tab_context())
        context['is_manager'] = self.is_manager(self.object)
        context['settings_tab'] = 'validation'
        if context['rules'] is None:
            context['url'] = reverse('api_v4:create_ra_rules')
            context['method'] = 'post'
        else:
            context['url'] = reverse('api_v4:ra_rules', args=[context['rules'].id])
            context['method'] = 'put'
        return context


class ConceptFilter(django_filters.FilterSet):
    registration_date = django_filters.DateFilter(field_name='statuses__registrationDate',
                                                  widget=BootstrapDateTimePicker,
                                                  method='filter_registration_date')

    status = django_filters.ChoiceFilter(choices=MDR.STATES,
                                         field_name='statuses__state',
                                         widget=Select(attrs={'class': 'form-control'}))

    class Meta:
        model = MDR._concept
        # Exclude unused fields, otherwise they appear in the template
        fields: list = []

    def filter_registration_date(self, queryset, name, value):
        selected_date = value

        # Return all the statuses that are valid at a particular date and then
        # filter on the concepts linked to a valid status.
        status_is_valid = Q(statuses__in=MDR.Status.objects.valid_at_date(when=selected_date))

        # Return only the statuses that are linked to the selected RA
        status_has_selected_ra = Q(statuses__registrationAuthority__id=self.registration_authority_id)

        return queryset.filter(status_is_valid & status_has_selected_ra).distinct()
    @property
    def qs(self):
        # Override the primary queryset to restrict to specific Registration Authority on page
        parent = super().qs

        return parent.filter(statuses__registrationAuthority__id=self.registration_authority_id)

    def __init__(self, *args, **kwargs):
        # Override the init method so we can pass the iid to the queryset
        self.registration_authority_id = kwargs.pop('registration_authority_id')
        super().__init__(*args, **kwargs)


class DateFilterView(FilterView, MainPageMixin):
    active_tab = 'data_dictionary'

    filterset_class = ConceptFilter
    template_name = 'aristotle_mdr/organization/registration_authority/data_dictionary.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context.update(self.get_tab_context())

        # Need to pass the ra context for use in building links in the template
        ra = MDR.RegistrationAuthority.objects.get(id=self.kwargs['iid'])
        context['item'] = ra
        context['is_manager'] = self.is_manager(ra)

        context['status'] = self.request.GET.get('status', MDR.STATES.standard)
        context['date'] = self.request.GET.get('registration_date', datetime.date.today())

        context['downloaders'] = self.build_downloaders(context['object_list'])

        return context

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs.update({'registration_authority_id': self.kwargs['iid']})

        if kwargs["data"] is None:
            # If there were no selections made in the form, set defaults
            kwargs["data"] = {"status": MDR.STATES.standard,
                              "registration_date": str(datetime.date.today())}

        return kwargs

    def build_downloaders(self, queryset):
        downloaders = fetch_aristotle_downloaders()

        options: list = []

        ids = [concept.id for concept in queryset]

        for dl in downloaders:
            query = QueryDict(mutable=True)
            query.setlist('items', ids)

            url = '{url}?{qstring}'.format(
                url=reverse('aristotle:download_options', args=[dl.download_type]),
                qstring=query.urlencode()
            )

            options.append({'label': dl.label, 'url': url})

        return options
