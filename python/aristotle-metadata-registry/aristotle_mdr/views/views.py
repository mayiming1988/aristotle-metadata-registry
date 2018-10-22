from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import PermissionDenied, FieldDoesNotExist, ObjectDoesNotExist
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, RedirectView
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.utils.dateparse import parse_datetime
from django.contrib.contenttypes.models import ContentType
from formtools.wizard.views import SessionWizardView

import json
import copy
from collections import defaultdict

import reversion
from reversion_compare.views import HistoryCompareDetailView

from aristotle_mdr.perms import (
    user_can_view, user_can_edit,
    user_can_change_status
)
from aristotle_mdr import perms
from aristotle_mdr.utils import url_slugify_concept, pretify_camel_case

from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR
from aristotle_mdr.utils import get_concepts_for_apps, fetch_aristotle_settings, fetch_aristotle_downloaders
from aristotle_mdr.views.utils import generate_visibility_matrix, CachePerItemUserMixin
from aristotle_mdr.contrib.slots.utils import get_allowed_slots
from aristotle_mdr.contrib.favourites.models import Favourite, Tag
from aristotle_mdr.managers import ConceptManager

from haystack.views import FacetedSearchView

from ckeditor_uploader.fields import RichTextUploadingField as RichTextField

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

PAGES_PER_RELATED_ITEM = 15


class SmartRoot(RedirectView):
    unauthenticated_pattern = None
    authenticated_pattern = None

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.pattern_name = self.authenticated_pattern
        else:
            self.pattern_name = self.unauthenticated_pattern
        return super().get_redirect_url(*args, **kwargs)


class DynamicTemplateView(TemplateView):
    def get_template_names(self):
        return ['aristotle_mdr/static/%s.html' % self.kwargs['template']]


class ConceptHistoryCompareView(HistoryCompareDetailView):
    model = MDR._concept
    pk_url_kwarg = 'iid'
    template_name = "aristotle_mdr/actions/concept_history_compare.html"

    compare_exclude = [
        'favourites',
        'user_view_history',
        'submitter',
        'is_public',
        'is_locked'
    ]

    item_action_url = 'aristotle:item_version'

    def get_object(self, queryset=None):
        item = super().get_object(queryset)
        if not user_can_view(self.request.user, item):
            raise PermissionDenied
        self.model = item.item.__class__  # Get the subclassed object
        return item

    # Overwrite this to add item url
    def _get_action_list(self):
        action_list = []
        versions = self._order_version_queryset(
            reversion.models.Version.objects.get_for_object(
                self.get_object()
            ).select_related("revision__user")
        )

        for version in versions:
            action_list.append({
                'version': version,
                'revision': version.revision,
                'url': reverse(self.item_action_url, args=[version.id])
            })
        return action_list

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def notification_redirect(self, content_type, object_id):

    ct = ContentType.objects.get(id=content_type)
    model_class = ct.model_class()
    obj = model_class.objects.get(id=object_id)
    return HttpResponseRedirect(obj.get_absolute_url())


def get_if_user_can_view(objtype, user, iid):
    item = get_object_or_404(objtype, pk=iid)
    if user_can_view(user, item):
        return item
    else:
        return False


def concept_by_uuid(request, uuid):
    item = get_object_or_404(MDR._concept, uuid=uuid)
    return redirect(url_slugify_concept(item))


def measure(request, iid, model_slug, name_slug):
    item = get_object_or_404(MDR.Measure, pk=iid).item
    return render(
        request, [item.template],
        {
            'item': item,
            # 'view': request.GET.get('view', '').lower(),
            # 'last_edit': last_edit
        }
    )

    # return render_if_user_can_view(MDR.Measure, *args, **kwargs)


class ConceptRenderMixin:
    """
    Class based view for rendering a concept, replaces render_if_condition_met
    **This should be used with a permission mixin or check_item override**

    slug_redirect determines wether /item/id redirects to /item/id/model_slug/name_slug
    """

    objtype = None
    itemid_arg = 'iid'
    modelslug_arg = 'model_slug'
    nameslug_arg = 'name_slug'
    slug_redirect = False

    def get_queryset(self):
        itemid = self.kwargs[self.itemid_arg]

        if self.objtype:
            model = self.objtype
        else:
            model = None
            # If we have a model_slug try using that
            model_slug = self.kwargs.get(self.modelslug_arg, '')
            if model_slug:
                try:
                    rel = MDR._concept._meta.get_field(model_slug)
                except FieldDoesNotExist:
                    rel = None

                # Check if it is an auto created one to one field
                if rel and rel.one_to_one and rel.auto_created and issubclass(rel.related_model, MDR._concept):
                    model = rel.related_model

        if model is None:
            model = type(MDR._concept.objects.get_subclass(id=itemid))

        return self.get_related(model)

    def get_item(self):
        itemid = self.kwargs[self.itemid_arg]
        queryset = self.get_queryset()
        try:
            item = queryset.get(pk=itemid)
        except ObjectDoesNotExist:
            item = None
        return item

    def get_related(self, model):
        """Return a queryset fetching related concepts"""

        related_fields = []
        prefetch_fields = ['statuses']
        for field in model._meta.get_fields():
            if field.is_relation and field.many_to_one and issubclass(field.related_model, MDR._concept):
                # If a field is a foreign key that links to a concept
                related_fields.append(field.name)
            elif field.is_relation and field.one_to_many and issubclass(field.related_model, MDR.AbstractValue):
                # If field is a reverse foreign key that links to an
                # abstract value
                prefetch_fields.append(field.name)

        return model.objects.select_related(*related_fields).prefetch_related(*prefetch_fields)

    def check_item(self, item):
        # To be overwritten
        return True

    def get_user(self):
        return self.request.user

    def get_redirect(self):

        if not self.modelslug_arg:
            model_correct = True
        else:
            model_slug = self.kwargs.get(self.modelslug_arg, '')
            model_correct = (self.item._meta.model_name == model_slug)

        name_slug = self.kwargs.get(self.nameslug_arg, '')
        # name_correct = (slugify(self.item.name) == name_slug)
        name_present = (name_slug is not None)

        if not model_correct or not name_present:
            return True, url_slugify_concept(self.item)
        else:
            return False, ''

    def dispatch(self, request, *args, **kwargs):
        self.item = self.get_item()

        if self.item is None:
            # If item was not found and no redirect was needed
            return HttpResponseNotFound()

        if self.slug_redirect:
            redirect, url = self.get_redirect()
            if redirect:
                return HttpResponseRedirect(url)

        self.user = self.get_user()
        result = self.check_item(self.item)
        if not result:
            if self.request.user.is_anonymous():
                redirect_url = '{}?next={}'.format(
                    reverse('friendly_login'),
                    self.request.path
                )
                return HttpResponseRedirect(redirect_url)
            else:
                return HttpResponseForbidden()

        from aristotle_mdr.contrib.view_history.signals import metadata_item_viewed
        metadata_item_viewed.send(sender=self.item, user=self.user.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        if self.request.user.is_anonymous():
            context['isFavourite'] = False
        else:
            context['isFavourite'] = self.request.user.profile.is_favourite(self.item)

        from reversion.models import Version
        context['last_edit'] = Version.objects.get_for_object(self.item).first()
        # Only display viewable slots
        context['slots'] = get_allowed_slots(self.item, self.user)
        context['item'] = self.item
        context['statuses'] = self.item.current_statuses
        context['discussions'] = self.item.relatedDiscussions.all()
        context['vue'] = True

        # Tags
        if self.request.user.is_authenticated():
            item_tags = Favourite.objects.filter(
                tag__profile=self.request.user.profile,
                tag__primary=False,
                item=self.item
            ).order_by('created').values_list('tag__name', flat=True)

            user_tags = Tag.objects.filter(
                profile=self.request.user.profile,
                primary=False
            ).values_list('name', flat=True)

            item_tags = list(item_tags)
            user_tags = list(user_tags)

            context['tags'] = {
                'item': item_tags,
                'user': user_tags
            }
        else:
            context['tags'] = {
                'item': [],
                'user': []
            }

        return context

    def get_template_names(self):
        default_template = "{}/concepts/{}.html".format(
            self.item.__class__._meta.app_label,
            self.item.__class__._meta.model_name
        )

        return [default_template, self.item.template]


# General concept view
class ConceptView(CachePerItemUserMixin, ConceptRenderMixin, TemplateView):

    slug_redirect = True
    cache_item_kwarg = 'iid'
    cache_view_name = 'ConceptView'

    def check_item(self, item):
        return user_can_view(self.request.user, item)


class DataElementView(ConceptRenderMixin, TemplateView):

    objtype = MDR.DataElement

    def check_item(self, item):
        return user_can_view(self.request.user, item)

    def get_related(self, model):
        related_objects = [
            'valueDomain',
            'dataElementConcept__objectClass',
            'dataElementConcept__property'
        ]
        prefetch_objects = [
            'valueDomain__permissiblevalue_set',
            'valueDomain__supplementaryvalue_set',
            'statuses'
        ]
        return model.objects.select_related(*related_objects).prefetch_related(*prefetch_objects)


class ConceptVersionView(ConceptRenderMixin, TemplateView):

    slug_redirect = False
    version_arg = 'verid'
    template_name = 'aristotle_mdr/concepts/managedContentVersion.html'
    concept_fields = ['references', 'submitting_organisation', 'responsible_organisation',
                      'origin', 'origin_URI', 'comments']
    default_weak_map = {
        'aristotle_mdr_slots.slot': 'concept',
        'aristotle_mdr_identifiers.scopedidentifier': 'concept'
    }

    def check_item(self, item):
        # Will 403 when user cant view the item
        return user_can_view(self.request.user, item)

    def get_item(self):
        # Gets the current item
        return self.item_version.object

    def get_matching_object_from_revision(self, revision, current_version, target_ct=None):
        # Finds another version in the same revision with same id
        current_ct = current_version.content_type
        version_filter = Q(revision=revision) &\
            Q(object_id=current_version.object_id) &\
            ~Q(content_type_id=current_ct.id)

        # Other versions in the revision could have the same id
        versions = reversion.models.Version.objects.filter(
            version_filter
        )

        target_version = None
        for sub_version in versions:
            ct = sub_version.content_type
            if target_ct is not None:
                if sub_version.content_type == target_ct:
                    target_version = sub_version
                    break
            else:
                if issubclass(ct.model_class(), MDR._concept):
                    # Find version that is a _concept subclass
                    # Since the pk is the _concept_ptr this is fine
                    target_version = sub_version
                    break

        return target_version

    def get_version(self):
        # Get the version of a concept and its matching subclass
        try:
            version = reversion.models.Version.objects.get(id=self.kwargs[self.version_arg])
        except reversion.models.Version.DoesNotExist:
            return False

        self.revision = version.revision
        concept_ct = ContentType.objects.get_for_model(MDR._concept)

        # If we got a concept version id
        if version.content_type == concept_ct:
            self.concept_version = version
            self.item_version = self.get_matching_object_from_revision(
                self.revision,
                version
            )
            if self.item_version is None:
                return False
        # If we got a concept subclass's version id
        elif issubclass(version.content_type.model_class(), MDR._concept):
            self.item_version = version
            self.concept_version = self.get_matching_object_from_revision(
                self.revision,
                version,
                concept_ct
            )
        else:
            return False

        self.concept_version_data = json.loads(self.concept_version.serialized_data)[0]
        self.item_version_data = json.loads(self.item_version.serialized_data)[0]
        self.item_model = self.item_version.content_type.model_class()

        return True

    def get_weak_versions(self, model):
        # Get version data for weak entites (reverse relations to an
        # aristotleComponent)

        pk = self.item_version_data['pk']

        # Find weak models create mapping of model labels to link fields
        weak_map = self.default_weak_map
        for field in model._meta.get_fields():
            if field.is_relation and field.one_to_many and\
                    issubclass(field.related_model, MDR.aristotleComponent):
                weak_map[field.related_model._meta.label_lower] = field.field.name

        if len(weak_map) == 0:
            return []

        # Get any models found before in the same revision to dict
        weak_items = self.get_related_versions(pk, weak_map)

        # Process into template friendly version
        template_weak_models = []
        for label, item_dict in weak_items.items():
            model = apps.get_model(label)

            template_weak_models.append({
                'model': pretify_camel_case(model.__name__),
                'headers': item_dict['headers'],
                'items': item_dict['items']
            })

        return template_weak_models

    def process_dict(self, fields, model):
        # Process fields dict, updating field names and links

        # Create replacement mapping fields to models
        replacements = {}
        for field in model._meta.get_fields():
            if field.is_relation and (field.many_to_one or field.many_to_many) and\
                    (issubclass(field.related_model, MDR._concept) or
                        issubclass(field.related_model, MDR.aristotleComponent)):
                replacements[field.name] = field.related_model

        # Create new mapping with user friendly keys and replaced models
        updated_fields = {}
        for key, value in fields.items():
            field = model._meta.get_field(key)
            header = field.verbose_name.title()

            replaced = False
            if key in replacements:

                sub_model = replacements[key]

                if type(value) == int and field.many_to_one:
                    updated_fields[header] = self.lookup_object([value], sub_model, field)
                    replaced = True
                elif type(value) == list and field.many_to_many and value:
                    updated_fields[header] = self.lookup_object(value, sub_model, field)
                    replaced = True

            if not replaced:
                updated_fields[header] = {
                    'is_link': False,
                    'value': value,
                    'help_text': field.help_text
                }

        return updated_fields

    def lookup_object(self, pk_list, sub_model, field):
        if issubclass(sub_model.objects.__class__, ConceptManager):
            objs = sub_model.objects.visible(self.request.user).filter(pk__in=pk_list)
        else:
            objs = sub_model.objects.filter(pk__in=pk_list)

        objs_repr = {
            'is_link': True,
            'help_text': field.help_text
        }

        if len(objs) <= 0:
            return {
                'is_link': False,
                'value': 'Linked to object(s) you do not have permission to view'
            }
        elif len(objs) == 1:
            objs_repr['object'] = objs[0]
            objs_repr['is_list'] = False

            if issubclass(sub_model, MDR.aristotleComponent):
                objs_repr['linkid'] = objs[0].parentItem.id
            else:
                objs_repr['linkid'] = objs[0].id
        else:
            objs_repr['object_list'] = list(objs)
            objs_repr['is_list'] = True

        return objs_repr

    def get_related_versions(self, pk, mapping):
        # mapping should be a mapping of model labels to fields on item

        related = {}
        # Add any models found before in the same revision to dict
        for version in self.revision.version_set.all():
            data = json.loads(version.serialized_data)[0]
            if data['model'] in mapping:

                if data['model'] not in related:
                    related[data['model']] = {
                        'items': []
                    }

                # There is a version in the revision that is of the correct
                # type. Need to check wether it links to the correct item
                related_model = apps.get_model(data['model'])

                # Find the field that links the weak model back to our model
                link_field = mapping[data['model']]

                if link_field and link_field in data['fields']:
                    # If it links back to the correct pk
                    if data['fields'][link_field] == pk:
                        # Add to weak models
                        del data['fields'][link_field]
                        final_fields = self.process_dict(data['fields'], related_model)

                        if 'headers' not in related[data['model']]:
                            headers = []
                            for header, item in final_fields.items():
                                headers.append({
                                    'text': header,
                                    'help_text': item.get('help_text', '')
                                })
                            related[data['model']]['headers'] = headers

                        related[data['model']]['items'].append(final_fields)

        return related

    def dispatch(self, request, *args, **kwargs):
        exists = self.get_version()
        if not exists:
            return HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def get_version_context_data(self):
        # Get the context data for this complete version

        version_dict = self.concept_version_data['fields']
        # Keys under item_data are used as headings
        version_dict['item_data'] = {'Names & References': {}}

        # Replace workgroup reference with wg object
        if version_dict['workgroup']:
            try:
                workgroup = MDR.Workgroup.objects.get(pk=version_dict['workgroup'])
            except MDR.Workgroup.DoesNotExist:
                workgroup = None

            version_dict['workgroup'] = workgroup

        # Add concept fields as "Names & References"
        for field in self.concept_fields:
            if field in self.concept_version_data['fields']:
                fieldobj = MDR._concept._meta.get_field(field)
                field_data = {
                    'is_link': False,
                    'is_html': False,
                    'value': self.concept_version_data['fields'][field],
                    'help_text': fieldobj.help_text
                }

                if issubclass(type(fieldobj), RichTextField):
                    field_data['is_html'] = True

                # Keys under item_data are used as headings
                version_dict['item_data']['Names & References'][fieldobj.verbose_name.title()] = field_data

        # Add some extra data the temlate expects from a regular item object
        version_dict['meta'] = {
            'app_label': self.item_version.content_type.app_label,
            'model_name': self.item_version.content_type.model
        }
        version_dict['id'] = self.item_version_data['pk']
        version_dict['pk'] = self.item_version_data['pk']
        version_dict['get_verbose_name'] = self.item_version.content_type.name.title()
        version_dict['created'] = parse_datetime(self.concept_version_data['fields']['created'])

        # Add weak entities and components
        version_dict['weak'] = self.get_weak_versions(self.item_model)
        components = self.process_dict(self.item_version_data['fields'], self.item_model)
        version_dict['item_data']['Components'] = components

        return version_dict

    def get_context_data(self, *args, **kwargs):
        context = super(ConceptRenderMixin, self).get_context_data(*args, **kwargs)
        context['hide_item_actions'] = True
        context['hide_item_supersedes'] = True
        context['hide_item_help'] = True
        context['hide_item_related'] = True
        context['item'] = self.get_version_context_data()
        context['current_item'] = self.item
        context['revision'] = self.revision
        context['item_is_version'] = True
        return context

    def get_template_names(self):
        return [self.template_name]


def registrationHistory(request, iid):
    item = get_if_user_can_view(MDR._concept, request.user, iid)
    if not item:
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied

    history = item.statuses.order_by("registrationAuthority", "-registrationDate")
    out = {}
    for status in history:
        if status.registrationAuthority in out.keys():
            out[status.registrationAuthority].append(status)
        else:
            out[status.registrationAuthority] = [status]

    return render(request, "aristotle_mdr/registrationHistory.html", {'item': item, 'history': out})


def unauthorised(request, path=''):
    if request.user.is_anonymous():
        return render(request, "401.html", {"path": path, "anon": True, }, status=401)
    else:
        return render(request, "403.html", {"path": path, "anon": True, }, status=403)


def not_found(request, path):
    context = {'anon': request.user.is_anonymous(), 'path': path}
    return render(request, "404.html", context)


def handler500(request, *args, **argv):
    return render(request, '500.html')


def create_list(request):
    if request.user.is_anonymous():
        return redirect(reverse('friendly_login') + '?next=%s' % request.path)
    if not perms.user_is_editor(request.user):
        raise PermissionDenied

    aristotle_apps = fetch_aristotle_settings().get('CONTENT_EXTENSIONS', [])
    aristotle_apps += ["aristotle_mdr"]
    out = {}

    wizards = []
    for wiz in getattr(settings, 'ARISTOTLE_SETTINGS', {}).get('METADATA_CREATION_WIZARDS', []):
        w = wiz.copy()
        _w = {
            'model': apps.get_app_config(wiz['app_label']).get_model(wiz['model']),
            'class': import_string(wiz['class']),
        }
        w.update(_w)
        wizards.append(w)

    for m in get_concepts_for_apps(aristotle_apps):
        # Only output subclasses of 11179 concept
        app_models = out.get(m.app_label, {'app': None, 'models': []})
        if app_models['app'] is None:
            try:
                app_models['app'] = getattr(apps.get_app_config(m.app_label), 'verbose_name')
            except:
                app_models['app'] = "No name"  # Where no name is configured in the app_config, set a dummy so we don't keep trying
        app_models['models'].append((m, m.model_class()))
        out[m.app_label] = app_models

    return render(
        request, "aristotle_mdr/create/create_list.html",
        {
            'models': sorted(out.values(), key=lambda x: x['app']),
            'wizards': wizards
        }
    )


def display_review(wizard):
    if wizard.display_review is not None:
        return wizard.display_review
    else:
        return True


class ReviewChangesView(SessionWizardView):

    items = None
    display_review = None

    # Override this
    change_step_name = None

    def get_form_kwargs(self, step):

        if step == 'review_changes':
            items = self.get_items()
            # Check some values from last step
            cleaned_data = self.get_change_data()
            cascade = cleaned_data['cascadeRegistration']
            state = cleaned_data['state']
            ra = cleaned_data['registrationAuthorities']

            static_content = {'new_state': state, 'new_reg_date': cleaned_data['registrationDate']}
            # Need to check wether cascaded was true here

            if cascade == 1:
                all_ids = []
                for item in items:

                    # Can't cascade from _concept
                    if isinstance(item, MDR._concept):
                        cascade = item.item.registry_cascade_items
                    else:
                        cascade = item.registry_cascade_items

                    cascaded_ids = [a.id for a in cascade]
                    cascaded_ids.append(item.id)
                    all_ids.extend(cascaded_ids)

                queryset = MDR._concept.objects.filter(id__in=all_ids)
            else:
                ids = [a.id for a in items]
                queryset = MDR._concept.objects.filter(id__in=ids)

            return {'queryset': queryset, 'static_content': static_content, 'ra': ra[0], 'user': self.request.user}

        return {}

    def get_form(self, step=None, data=None, files=None):

        self.set_review_var(step, data, files, self.change_step_name)
        return super().get_form(step, data, files)

    def get_change_data(self):
        # We override this when the change_data doesnt come form a form
        return self.get_cleaned_data_for_step(self.change_step_name)

    def set_review_var(self, step, data, files, change_step):

        # Set step if it's None
        if step is None:
            step = self.steps.current

        if step == change_step and data:
            review = True
            if data.get('submit_next'):
                review = True
            elif data.get('submit_skip'):
                review = False

            self.display_review = review

    def get_items(self):
        return self.items

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        if self.steps.current == 'review_changes':
            data = self.get_cleaned_data_for_step(self.change_step_name)
            if 'registrationAuthorities' in data:
                context.update({'ra': data['registrationAuthorities'][0]})

        return context

    def register_changes(self, form_dict, change_form=None, **kwargs):

        items = self.get_items()

        try:
            review_data = form_dict['review_changes'].cleaned_data
        except KeyError:
            review_data = None

        if review_data:
            selected_list = review_data['selected_list']

        # process the data in form.cleaned_data as required
        if change_form:
            cleaned_data = form_dict[change_form].cleaned_data
        else:
            cleaned_data = self.get_change_data(register=True)

        ras = cleaned_data['registrationAuthorities']
        state = cleaned_data['state']
        regDate = cleaned_data['registrationDate']
        cascade = cleaned_data['cascadeRegistration']
        changeDetails = cleaned_data['changeDetails']

        if changeDetails is None:
            changeDetails = ""

        success = []
        failed = []

        arguments = {
            'state': state,
            'user': self.request.user,
            'changeDetails': changeDetails,
            'registrationDate': regDate,
        }

        if review_data:
            for ra in ras:
                arguments['items'] = selected_list
                status = ra.register_many(**arguments)
                success.extend(status['success'])
                failed.extend(status['failed'])
        else:
            for item in items:
                for ra in ras:
                    # Should only be 1 ra
                    # Need to check before enforcing

                    # Can't cascade from _concept
                    if isinstance(item, MDR._concept):
                        arguments['item'] = item.item
                    else:
                        arguments['item'] = item

                    if cascade:
                        register_method = ra.cascaded_register
                    else:
                        register_method = ra.register

                    status = register_method(**arguments)
                    success.extend(status['success'])
                    failed.extend(status['failed'])

        return (success, failed)

    def register_changes_with_message(self, form_dict, change_form=None, *args, **kwargs):

        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.request.user)

            success, failed = self.register_changes(form_dict, change_form)

            bad_items = sorted([str(i.id) for i in failed])
            count = self.get_items().count()

            if failed:
                message = _(
                    "%(num_items)s items registered \n"
                    "%(num_faileds)s items failed, they had the id's: %(bad_ids)s"
                ) % {
                    'num_items': count,
                    'num_faileds': len(failed),
                    'bad_ids': ",".join(bad_items)
                }
            else:
                message = _(
                    "%(num_items)s items registered\n"
                ) % {
                    'num_items': count,
                }

            reversion.revisions.set_comment(message)

        return message


class ChangeStatusView(ReviewChangesView):

    change_step_name = 'change_status'

    form_list = [
        ('change_status', MDRForms.ChangeStatusForm),
        ('review_changes', MDRForms.ReviewChangesForm)
    ]

    templates = {
        'change_status': 'aristotle_mdr/actions/changeStatus.html',
        'review_changes': 'aristotle_mdr/actions/review_state_changes.html'
    }

    condition_dict = {'review_changes': display_review}

    display_review = None

    def dispatch(self, request, *args, **kwargs):
        # Check for keyError here
        self.item = get_object_or_404(MDR._concept, pk=kwargs['iid']).item

        if not (self.item and user_can_change_status(request.user, self.item)):
            if request.user.is_anonymous():
                return redirect(reverse('friendly_login') + '?next=%s' % request.path)
            else:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_items(self):
        return [self.item]

    def get_form_kwargs(self, step):

        kwargs = super().get_form_kwargs(step)

        if step == 'change_status':
            return {'user': self.request.user}

        return kwargs

    def get_context_data(self, form, **kwargs):
        item = self.item
        status_matrix = json.dumps(generate_visibility_matrix(self.request.user))
        context = super().get_context_data(form, **kwargs)
        context.update({'item': item, 'status_matrix': status_matrix})
        return context

    def done(self, form_list, form_dict, **kwargs):
        self.register_changes(form_dict, 'change_status')
        return HttpResponseRedirect(url_slugify_concept(self.item))


def extensions(request):
    content=[]
    aristotle_apps = fetch_aristotle_settings().get('CONTENT_EXTENSIONS', [])

    if aristotle_apps:
        for app_label in aristotle_apps:
            app=apps.get_app_config(app_label)
            try:
                app.about_url = reverse('%s:about' % app_label)
            except:
                pass  # if there is no about URL, thats ok.
            content.append(app)

    content = list(set(content))
    aristotle_downloads = fetch_aristotle_downloaders()
    downloads=[]
    if aristotle_downloads:
        for download in aristotle_downloads:
            downloads.append(download())

    return render(
        request,
        "aristotle_mdr/static/extensions.html",
        {'content_extensions': content, 'download_extensions': downloads, }
    )
