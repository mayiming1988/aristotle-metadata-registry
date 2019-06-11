from django.apps import apps
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.core.exceptions import FieldDoesNotExist

from aristotle_mdr import models as MDR
from aristotle_mdr.utils.text import pretify_camel_case
from aristotle_mdr.views.views import ConceptRenderView
from aristotle_mdr.perms import user_can_view, user_can_edit
from aristotle_mdr.contrib.publishing.models import VersionPermissions
from aristotle_mdr.constants import visibility_permission_choices as VISIBILITY_PERMISSION_CHOICES
from aristotle_mdr.views.utils import SimpleItemGet

import json
import reversion
import diff_match_patch

from collections import defaultdict
from ckeditor_uploader.fields import RichTextUploadingField as RichTextField

import logging
logger = logging.getLogger(__name__)


class VersionField:
    """
    Field for use in previous version display
    With fancy dereferencing
    Template to render in helpers/version_field.html

    Doesn't deal with lists of components (no many to many's for those)
    """

    perm_message = 'Linked to object(s) you do not have permission to view'

    def __init__(self, value='', obj=None, help_text='', html=False, reference_label=''):
        if not value:
            self.value = ''
        else:
            self.value=str(value)

        if type(obj) == list and len(obj) == 1:
            self.obj = obj[0]
        else:
            self.obj=obj

        self.help_text=help_text
        self.is_html=html
        self.reference_label = reference_label

    def dereference(self, lookup):
        # Lookup ids in a given dictionary
        if self.is_reference:
            replaced = False
            if self.reference_label in lookup:
                id_lookup = lookup[self.reference_label]
                if self.is_list:
                    # No perm message for these
                    deref_list = []
                    for pk in self.obj:
                        if pk in id_lookup:
                            deref_list.append(id_lookup[pk])
                    self.obj = deref_list
                    replaced = True
                else:
                    if self.obj in id_lookup:
                        self.obj = id_lookup[self.obj]
                        replaced = True

            if not replaced:
                self.obj = None
                self.value = self.perm_message

            self.reference_label = ''

    @property
    def is_reference(self):
        return self.reference_label != ''

    @property
    def is_link(self):
        return (not self.is_reference and bool(self.obj))

    @property
    def is_list(self):
        return (type(self.obj) == list)

    @property
    def object_list(self):
        if self.is_list:
            return self.obj
        else:
            return []

    @property
    def link_id(self):
        if not self.is_link or self.is_list:
            return None

        if issubclass(self.obj.__class__, MDR.aristotleComponent):
            return self.obj.parentItemId
        else:
            return self.obj.id

    def __str__(self):
        if self.is_link:
            if hasattr(self.obj, 'name'):
                return self.obj.name
            else:
                # Shouldn't actually happen, but just in case
                return str(self.obj)
        else:
            return self.value or 'None'


class ConceptVersionView(ConceptRenderView):
    """ Display the version of a concept at a particular point"""
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
        # Will 403 Forbidden when user can't view the item
        return user_can_view(self.request.user, item)

    def get_item(self):
        # Gets the current item
        return self.item_version.object

    def get_matching_object_from_revision(self, revision, current_version, target_ct=None):
        # Finds another version in the same revision with same id
        current_ct_id = current_version.content_type_id
        version_filter = Q(revision=revision) &\
            Q(object_id=current_version.object_id) &\
            ~Q(content_type_id=current_ct_id)

        # Other versions in the revision could have the same id
        versions = reversion.models.Version.objects.filter(
            version_filter
        )

        target_version = None
        for sub_version in versions:
            if target_ct is not None:
                ctid = sub_version.content_type_id
                if ctid == target_ct.id:
                    target_version = sub_version
                    break
            else:
                ct = sub_version.content_type
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
        if version.content_type_id == concept_ct.id:
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
            if field.is_relation and field.one_to_many and \
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

            if 'headers' in item_dict:
                headers = item_dict['headers']
            else:
                headers = []
            template_weak_models.append({
                'model': pretify_camel_case(model.__name__),
                'headers': item_dict.get('headers', []),
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
                updated_fields[header] = VersionField(
                    value=value,
                    help_text=field.help_text
                )

        return updated_fields

    def lookup_object(self, pk_list, sub_model, field):

        if issubclass(sub_model, MDR._concept):
            label = MDR._concept._meta.label_lower
        else:
            label = sub_model._meta.label_lower

        self.obj_ids[label] += pk_list

        ver_field = VersionField(
            help_text=field.help_text,
            obj=pk_list,
            reference_label=label
        )

        return ver_field

    def lookup_object_refs(self):
        for label, id_list in self.obj_ids.items():
            model = apps.get_model(label)

            if issubclass(model, MDR._concept):
                object_qs = model.objects.visible(self.request.user).filter(id__in=id_list)
            else:
                object_qs = model.objects.filter(id__in=id_list)

            object_map = {}
            for obj in object_qs:
                object_map[obj.id] = obj

            self.fetched_objects[label] = object_map

    def replace_object_refs(self, field_dict):
        # Don't need to return the dict, passed as reference
        for key in field_dict.keys():
            field_dict[key].dereference(self.fetched_objects)

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
                # type. Need to check whether it links to the correct item
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
                                    'help_text': item.help_text
                                })
                            related[data['model']]['headers'] = headers

                        related[data['model']]['items'].append(final_fields)

        return related

    def dispatch(self, request, *args, **kwargs):
        # Dict mapping models to a list of ids
        self.obj_ids = defaultdict(list)
        # Dict mapping model -> id -> object
        self.fetched_objects = {}

        try:
            exists = self.get_version()
        except json.JSONDecodeError:
            # Handle invalid json
            return self.invalid_version(request, *args, **kwargs)

        if not exists:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def invalid_version(self, request, *args, **kwargs):
        # What to do when the version could not be deserialized
        logger.error('Version could not be loaded')
        try:
            version = reversion.models.Version.objects.get(id=self.kwargs[self.version_arg])
        except reversion.models.Version.DoesNotExist:
            raise Http404

        current = version.object
        if not self.check_item(current):
            raise PermissionDenied

        messages.warning(request, 'Version could not be loaded')

        return HttpResponseRedirect(
            reverse('aristotle:item_history', args=[current.id])
        )

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
                try:
                    fieldobj = MDR._concept._meta.get_field(field)
                except FieldDoesNotExist:
                    # The field doesn't exist on the new version, don't do anything
                    pass
                is_html = (issubclass(type(fieldobj), RichTextField))
                field = VersionField(
                    value=self.concept_version_data['fields'][field],
                    help_text=fieldobj.help_text,
                    html=is_html
                )

                # Keys under item_data are used as headings
                version_dict['item_data']['Names & References'][fieldobj.verbose_name.title()] = field

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
        weak = self.get_weak_versions(self.item_model)
        components = self.process_dict(self.item_version_data['fields'], self.item_model)
        self.lookup_object_refs()
        self.replace_object_refs(components)

        for i in range(len(weak)):
            for j in range(len(weak[i]['items'])):
                self.replace_object_refs(weak[i]['items'][j])

        version_dict['weak'] = weak
        version_dict['item_data']['Components'] = components

        return version_dict

    def get_context_data(self, *args, **kwargs):
        context = kwargs
        context['view'] = self
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


class ViewableVersionsMixin:
    def get_versions(self, metadata_item):

        versions = reversion.models.Version.objects.get_for_object(metadata_item).select_related("revision__user")

        in_workgroup = (metadata_item.workgroup and self.request.user in metadata_item.workgroup.member_list)
        authenticated_user = (not self.request.user.is_anonymous())

        # Determine the viewing permissions of the users
        if not self.request.user.is_superuser:
            # Superusers can see everything
            for version in versions:
                version_permission = VersionPermissions.objects.get_object_or_none(version=version)

                if version_permission is None:
                    # Default to applying workgroup permissions
                    if not in_workgroup:
                        versions = versions.exclude(pk=version.pk)
                else:
                    visibility = int(version_permission.visibility)

                    if visibility == VISIBILITY_PERMISSION_CHOICES.workgroup:
                        # Apply workgroup permissions
                        if not in_workgroup:
                            versions = versions.exclude(pk=version.pk)

                    elif visibility == VISIBILITY_PERMISSION_CHOICES.auth:
                        # Exclude anonymous users
                        if not authenticated_user:
                            versions = versions.exclude(pk=version.pk)

                    else:
                        # Visibility is public, don't exclude this version
                        pass

        versions = versions.order_by('-revision__date_created')

        return versions


class ConceptVersionCompareView(TemplateView, SimpleItemGet, ViewableVersionsMixin):
    """
    View that performs the historical comparision between two different versions of the same concept
    """
    template_name = 'aristotle_mdr/compare/compare.html'

    first_version_kwarg = 'fvid'
    second_version_kwarg = 'svid'

    field_to_diff = {}

    def get_concept(self):
        return self.get_item(self.request.user)

    def get_json(self, pk):
        version = reversion.models.Version.objects.get(pk=pk)
        data = json.loads(version.serialized_data)
        # We're only really interested in the fields
        return data[0]['fields']

    def generate_diff(self, first_json, second_json):
        # Because of how difflib works the first json must be the earlier version
        # We only need to iterate one time because the fields should be consistent across
        # the JSON serialized_data
        DiffMatchPatch = diff_match_patch.diff_match_patch()

        for field in first_json:
            first_value = first_json[field]

            second_value = ''
            if field in second_json:
                second_value = second_json[field]

            if isinstance(first_value, str) or isinstance(first_value, int):
                # No special treatment required
                diff = DiffMatchPatch.diff_main(str(first_value), str(second_value))
                DiffMatchPatch.diff_cleanupSemantic(diff)
                self.field_to_diff[field] = diff

            if isinstance(first_value, dict):
                # TODO: implment recursive behavior for this
                pass
        raise ValueError(self.field_to_diff)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        first_json = self.get_json(kwargs.pop(self.first_version_kwarg))
        second_json = self.get_json(kwargs.pop(self.second_version_kwarg))

        self.generate_diff(first_json, second_json)

        context['diffs'] = self.field_to_diff
        context['item'] = self.get_concept().item
        context['activetab'] = 'history'

        return context


class ConceptVersionListView(ListView, SimpleItemGet, ViewableVersionsMixin):
    """
    View  that lists all the specific versions of a particular concept
    """
    template_name = 'aristotle_mdr/compare/versions.html'
    item_action_url = 'aristotle:item_version'

    def get_object(self):
        item = self.get_item(self.request.user)
        self.model = item.item.__class__  # Get the subclassed object
        return item

    def get_queryset(self):
        """Return a queryset of all the versions the user has permission to access as well as associated metadata
         involved in template rendering"""
        metadata_item = self.get_object()
        versions = self.get_versions(metadata_item)

        version_list = []
        for version in versions:
            # TODO: move to bulk lookup for performance
            version_permission = VersionPermissions.objects.get_object_or_none(version=version)

            if version_permission is None:
                # Default to workgroup level permissions
                version_permission_code = 0
            else:
                version_permission_code = version_permission.visibility

            version_list.append({
                'permission': int(version_permission_code),
                'version': version,
                'revision': version.revision,
                'url': reverse(self.item_action_url, args=[version.id])
            })

        return version_list

    def get_context_data(self, **kwargs):
        # Determine the editing permissions of the user
        metadata_item = self.get_object()
        USER_CAN_EDIT = user_can_edit(self.request.user, metadata_item)

        context = {'activetab': 'history',
                   'user_can_edit': USER_CAN_EDIT,
                   'object': self.get_object(),
                   'item': self.get_object().item,
                   'versions': self.get_queryset()}

        return context
