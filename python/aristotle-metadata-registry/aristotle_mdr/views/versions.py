from typing import Dict, List, Optional, Tuple, Any
from django.apps import apps
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q, Model, Field
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import get_object_or_404

from aristotle_mdr import models as MDR
from aristotle_mdr.utils.text import pretify_camel_case
from aristotle_mdr.views.views import ConceptRenderView
from aristotle_mdr.perms import user_can_view, user_can_edit
from aristotle_mdr.contrib.publishing.models import VersionPermissions
from aristotle_mdr.constants import visibility_permission_choices as VISIBILITY_PERMISSION_CHOICES
from aristotle_mdr.views.utils import SimpleItemGet
from aristotle_mdr.utils.utils import strip_tags

import json
import reversion
import diff_match_patch

from collections import defaultdict
from ckeditor_uploader.fields import RichTextUploadingField as RichTextField

import logging
logger = logging.getLogger(__name__)


class VersionsMixin:
    def user_can_view_version(self, metadata_item, version_permission):
        """ Determine whether or not user can view the specific version """
        in_workgroup = metadata_item.workgroup and self.request.user in metadata_item.workgroup.member_list
        authenticated_user = not self.request.user.is_anonymous()

        if self.request.user.is_superuser:
            # Superusers can see everything
            return True

        if metadata_item.stewardship_organisation is None \
                and metadata_item.workgroup is None and metadata_item.submitter_id == self.request.user.id:
            # If you submitted the item and it has not been passed onto a workgroup or stewardship organisation
            return True

        if version_permission is None:
            # Default to applying workgroup permissions
            if in_workgroup:
                return True
        else:
            visibility = int(version_permission.visibility)

            if visibility == VISIBILITY_PERMISSION_CHOICES.workgroup:
                # Apply workgroup permissions
                if in_workgroup:
                    return True

            elif visibility == VISIBILITY_PERMISSION_CHOICES.auth:
                # Exclude anonymous users
                if authenticated_user:
                    return True
            else:
                # Visibility is public, don't exclude
                return True

        return False

    def get_versions(self, metadata_item):
        """ Get versions and apply permission checking so that only versions that the user is allowed to see are
        shown"""
        versions = reversion.models.Version.objects.get_for_object(metadata_item).select_related("revision__user")

        # Determine the viewing permissions of the users
        if not self.request.user.is_superuser:
            # Superusers can see everything, for performance we won't look up version permission objs
            version_to_permission = VersionPermissions.objects.in_bulk(versions)

            for version in versions:
                if version.id in version_to_permission:
                    version_permission = version_to_permission[version.id]
                else:
                    version_permission = None
                if not self.user_can_view_version(metadata_item, version_permission):
                    versions = versions.exclude(pk=version.pk)

        versions = versions.order_by('-revision__date_created')

        return versions

    def is_field_html(self, fieldname: str, model: Model) -> bool:
        fieldobj = model._meta.get_field(fieldname)
        return self.is_field_obj_html(fieldobj)

    def is_field_obj_html(self, field: Field) -> bool:
        return issubclass(type(field), RichTextField)

    def get_model_from_foreign_key_field(self, parent_model: Model, field) -> Model:
        try:
            return parent_model._meta.get_field(field).related_model
        except FieldDoesNotExist:
            return parent_model._meta.get_field(self.clean_field(field)).related_model

    def clean_field(self, field: str) -> str:
        postfix = '_set'
        if field.endswith(postfix):
            return field[:-len(postfix)]
        return field

    def get_field(self, field_name: str, model):
        try:
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist:
            field = model._meta.get_field(self.clean_field(field_name))

        return field

    def get_user_friendly_field_name(self, field: str, model):
        # If the field ends with _set we want to remove it, so we can look it up in the _meta.
        fieldobj = self.get_field(field, model)
        try:
            name = self.get_verbose_name(fieldobj)
        except AttributeError:
            name = field

        return name

    def get_verbose_name(self, field: Field):
        name: str
        if field.is_relation:
            name = field.related_model._meta.verbose_name
        else:
            name = field.name
        return name.title()


class VersionField:
    """
    Field for use in previous version display
    With fancy dereferencing
    Template to render in helpers/version_field.html
    """

    link: bool = False
    group: bool = False

    def __init__(self, fname: str, value, html=False):
        self.fname = fname
        self.value = str(value)
        self.is_html = html

    @property
    def is_link(self):
        return self.link

    @property
    def is_group(self):
        return self.group

    @property
    def heading(self):
        return self.fname

    def __str__(self):
        return self.value or 'None'


class VersionGroupField(VersionField):
    """Field with groups of subfields"""
    link = False
    group = True
    is_html = False

    def __init__(self, fname: str, subfields: List[List[VersionField]]):
        self.fname = fname
        self.subfields = subfields

    def __str__(self):
        return '{} sub items'.format(len(self.subfields))


class VersionLinkField(VersionField):
    """Version field that links to a concept or concept subclass"""

    link = True
    group = False
    is_html = False
    perm_message = 'Linked to object you do not have permission to view'
    subfields: List[Field] = []

    def __init__(self, fname: str, id: Optional[int], concept):
        self.fname = fname
        self.id = id

        if id is not None:
            if concept:
                # If field is set and we got a concept
                self.value = concept.name
                self.id = concept.id
            else:
                # If field is set but concept is None no perm
                self.value = self.perm_message
        else:
            # Set value empty if id is None
            self.value = ''

    @property
    def url(self):
        if self.id:
            return reverse('aristotle:item', args=[self.id])
        return ''


class ConceptVersionView(VersionsMixin, ConceptRenderView):
    """ Display the version of a concept at a particular point"""
    slug_redirect = False
    version_arg = 'verid'
    template_name = 'aristotle_mdr/concepts/managedContentVersion.html'
    # Top level fields to exclude
    excluded_fields = ['id', 'uuid', 'name', 'version', 'submitter', 'created', 'modified', 'serialized_model']

    def dispatch(self, request, *args, **kwargs):
        self.version = self.get_version()
        self.model = self.version.content_type.model_class()

        # Check it's a concept version
        if not issubclass(self.model, MDR._concept):
            raise Http404

        # Get version permission
        try:
            self.version_permission = VersionPermissions.objects.get(pk=self.version.pk)
        except VersionPermissions.DoesNotExist:
            self.version_permission = None

        # Deserialize version data
        try:
            self.version_dict = json.loads(self.version.serialized_data)
        except json.JSONDecodeError:
            # Handle bad serialized data
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def check_item(self, item):
        # Will 403 Forbidden when user can't view the version
        return self.user_can_view_version(item, self.version_permission)

    def get_item(self):
        # Gets the current item
        return self.version.object

    def get_version(self) -> reversion.models.Version:
        # Get the version objet
        return get_object_or_404(reversion.models.Version, id=self.kwargs[self.version_arg])

    def is_concept_fk(self, field):
        return field.many_to_one and issubclass(field.related_model, MDR._concept)

    def get_field_data(self, version_data: Dict, model, exclude=True) -> List[Tuple[Field, Any]]:
        """Get dict as list of tuples of field and it's data (recursively)"""
        field_data = []
        for name, data in version_data.items():
            # If field name isnt excluded or we are not excluding
            if name not in self.excluded_fields or not exclude:
                field: Field = self.get_field(name, model)
                # If field is subserialized
                if type(data) == list and field.is_relation:
                    sub_field_data = []
                    submodel = field.related_model
                    # Recursively resolve sub dicts
                    for subdata in data:
                        if type(subdata) == dict:
                            sub_field_data.append(
                                self.get_field_data(subdata, submodel, False)
                            )
                    # Add back as a list
                    field_data.append((field, sub_field_data))
                else:
                    field_data.append((field, data))

        return field_data

    def get_viewable_concepts(self, field_data: List) -> Dict[int, MDR._concept]:
        """Get all concepts linked from this version that are viewable by the user"""
        ids = []
        for field, data in field_data:
            # If foreign key to concept
            if self.is_concept_fk(field):
                ids.append(data)

            if type(data) == list:
                for subdata in data:
                    for field, subvalue in subdata:
                        if self.is_concept_fk(field):
                            ids.append(subvalue)

        return MDR._concept.objects.filter(id__in=ids).visible(self.request.user).in_bulk()

    def get_version_fields(self, field_data, concepts: Dict[int, MDR._concept]) -> List[VersionField]:
        """Get a list of VersionField objects to render"""
        fields: List[VersionField] = []
        for field, data in field_data:
            if self.is_concept_fk(field):
                fields.append(
                    VersionLinkField(self.get_verbose_name(field), data, concepts.get(data, None))
                )
            elif type(data) == list:
                # If field groups other items get their fields
                sub_fields: List[List[Field]] = []
                for subdata in data:
                    sub_fields.append(
                        self.get_version_fields(subdata, concepts)
                    )
                # Add group field
                fields.append(
                    VersionGroupField(self.get_verbose_name(field), sub_fields)
                )
            else:
                # If not foreign key or group
                fields.append(
                    VersionField(self.get_verbose_name(field), data, self.is_field_obj_html(field))
                )
        return fields

    def get_version_context_data(self) -> Dict:
        # Get the context data for this complete version
        context: dict = {}

        # Get field data
        field_data = self.get_field_data(self.version_dict, self.model)

        # Build item data
        viewable_concepts = self.get_viewable_concepts(field_data)
        context['item_fields'] = self.get_version_fields(field_data, viewable_concepts)

        # Set workgroup object
        if self.version_dict['workgroup']:
            try:
                workgroup = MDR.Workgroup.objects.get(pk=self.version_dict['workgroup'])
            except MDR.Workgroup.DoesNotExist:
                workgroup = None

            context['workgroup'] = workgroup

        # Add some extra data the template expects from a regular item object
        context['meta'] = {
            'app_label': self.version.content_type.app_label,
            'model_name': self.version.content_type.model
        }
        context.update({
            'id': self.version.object_id,
            'pk': self.version.object_id,
            'uuid': self.version_dict.get('uuid', ''),
            'name': self.version_dict.get('name', ''),
            'get_verbose_name': self.version.content_type.name.title(),
            'created': parse_datetime(self.version_dict['created']),
        })

        return context

    def get_context_data(self, *args, **kwargs):
        context = kwargs
        context.update({
            'view': self,
            'hide_item_actions': True,
            'hide_item_supersedes': True,
            'hide_item_help': True,
            'hide_item_related': True,
            'item_is_version': True,
            'item': self.get_version_context_data(),
            'current_item': self.item,
            'version': self.version,
            'revision': self.version.revision,
        })
        return context

    def get_template_names(self):
        return [self.template_name]


class ConceptVersionCompareView(SimpleItemGet, VersionsMixin, TemplateView):
    """
    View that performs the historical comparision between two different versions of the same concept
    """
    template_name = 'aristotle_mdr/compare/compare.html'
    context: dict = {}
    hidden_diff_fields = ['modified']

    def get_model(self, concept) -> Model:
        return concept.item._meta.model

    def handle_compare_failure(self):
        self.context['cannot_compare'] = True
        return self.context

    def get_differing_fields(self, earlier_dict, later_dict):
        # Iterate across the two and find the differing fields
        pass

    def generate_diff(self, earlier_dict, later_dict, raw=False) -> Dict[str, List[Tuple]]:
        """
        Returns a dictionary containing a list of tuples with the differences per field.
        The first element of the tuple specifies if it is an insertion (1), a deletion (-1), or an equality (0).

        Example:
        {field: [(0, hello), (1, world)]}

        """
        DiffMatchPatch = diff_match_patch.diff_match_patch()
        field_to_diff = {}

        for field in earlier_dict:
            # Iterate through all fields in the JSON
            if field not in self.hidden_diff_fields:
                # Don't show fields like modified, which are set by the database
                earlier_value = earlier_dict[field]
                later_value = later_dict[field]

                if earlier_value != later_value:
                    # No point doing diffs if there is no difference
                    if isinstance(earlier_value, str) or isinstance(earlier_value, int):
                        # No special treatment required for strings and int
                        earlier = str(earlier_value)
                        later = str(later_value)

                        if not raw:
                            # Strip tags if it's not raw
                            earlier = strip_tags(earlier)
                            later = strip_tags(later)

                        # Do the diff
                        diff = DiffMatchPatch.diff_main(earlier, later)
                        DiffMatchPatch.diff_cleanupSemantic(diff)

                        is_html_field = self.is_field_html(field, self.model)

                        field_to_diff[field] = {'user_friendly_name': field.title(),
                                                'subitem': False,
                                                'is_html': is_html_field,
                                                'diffs': diff}

                    elif isinstance(earlier_value, dict):
                        # It's a single subitem
                        subitem_model = self.get_model_from_foreign_key_field(self.model, self.clean_field(field))
                        field_to_diff[field] = {
                            'user_friendly_name': self.get_user_friendly_field_name(field, self.model),
                            'subitem': True,
                            'diffs': self.build_diff_of_subitem_dict(earlier_value, later_value,
                                                                     subitem_model, raw=raw)
                        }
                    elif isinstance(earlier_value, list):
                        # It's a list of subitems
                        subitem_model = self.get_model_from_foreign_key_field(self.model, field)
                        field_to_diff[field] = {
                            'user_friendly_name': self.get_user_friendly_field_name(field, self.model),
                            'subitem': True,
                            'diffs': self.build_diff_of_subitems(earlier_value, later_value, subitem_model, raw=raw)}

        return field_to_diff

    def generate_diff_for_added_removed_fields(self, ids, values, subitem_model, added=True, raw=False):
        """ Generates the diff for fields that have been added/removed from a concept comparision"""
        difference_dict = {}

        for id in ids:
            item = values[id]
            for field, value in item.items():
                if field == 'id':
                    pass
                else:
                    if not raw:
                        value = strip_tags(str(value))
                    # Because DiffMatchPatch returns a list of tuples of diffs
                    # for consistent display we also return a list of tuples of diffs
                    if added:
                        difference_dict[field] = {'is_html': self.is_field_html(field, subitem_model),
                                                  'diff': [(1, value)]}
                    else:
                        difference_dict[field] = {'is_html': self.is_field_html(field, subitem_model),
                                                  'diff': [(-1, value)]}
        return difference_dict

    def build_diff_of_subitem_dict(self, earlier_item, later_item, subitem_model, raw=False) -> List[Dict]:
        differences = []
        DiffMatchPatch = diff_match_patch.diff_match_patch()
        difference_dict = {}

        for field, earlier_value in earlier_item.items():
            if field == 'id':
                pass
            else:
                later_value = later_item[field]
                if not raw:
                    earlier_value = strip_tags(str(earlier_value))
                    later_value = strip_tags(str(later_value))

                if earlier_value is None:
                    # Can't perform a diff on a null value
                    earlier_value = 'None'

                if later_value is None:
                    later_value = 'None'

                diff = DiffMatchPatch.diff_main(earlier_value, later_value)
                DiffMatchPatch.diff_cleanupSemantic(diff)

                difference_dict[field] = {'is_html': self.is_field_html(field, subitem_model), 'diff': diff}

            differences.append(difference_dict)
        return differences

    def build_diff_of_subitems(self, earlier_values, later_values, subitem_model, raw=False) -> List[Dict]:
        """
        Given a list of dictionaries containing representations of objects, iterates through and returns a list of
        difference dictionaries per field
        Example:
            [{'field': [(0, hello), (1, world)], 'other_field': [(0, goodbye), (-1, world)]]
        """
        differences = []

        # Blame Google for this unpythonic variable
        DiffMatchPatch = diff_match_patch.diff_match_patch()

        both_empty = earlier_values == [] and later_values == []
        if not both_empty:

            earlier_items = {item['id']: item for item in earlier_values}
            later_items = {item['id']: item for item in later_values}

            # Items that are in the later items but not the earlier items have been 'added'
            added_ids = set(later_items.keys()) - set(earlier_items.keys())
            differences.append(
                self.generate_diff_for_added_removed_fields(added_ids, later_items, subitem_model, added=True,
                                                            raw=raw))

            # Items that are in the earlier items but not the later items have been 'removed'
            removed_ids = set(earlier_items.keys()) - set(later_items.keys())
            differences.append(
                self.generate_diff_for_added_removed_fields(removed_ids, earlier_items, subitem_model, added=False,
                                                            raw=raw))

            # Items with IDs that are present in both earlier and later data have been changed,
            # so we waFnt to perform a field-by-field dict comparision
            changed_ids = set(earlier_items).intersection(set(later_items))
            for id in changed_ids:
                earlier_item = earlier_items[id]
                later_item = later_items[id]

                difference_dict = {}

                for field, earlier_value in earlier_item.items():
                    later_value = later_item[field]

                    earlier_value = str(earlier_value)
                    later_value = str(later_value)

                    if not raw:
                        earlier_value = strip_tags(earlier_value)
                        later_value = strip_tags(later_value)

                    diff = DiffMatchPatch.diff_main(earlier_value, later_value)
                    DiffMatchPatch.diff_cleanupSemantic(diff)

                    difference_dict[field] = {'is_html': self.is_field_html(field, subitem_model),
                                              'diff': diff}
                differences.append(difference_dict)

        return differences

    def get_version_jsons(self, first_version, second_version) -> Tuple:
        """
        Diffing is order sensitive, so date comparision is performed to ensure that the versions are compared with
        correct chronology.
        """
        first_version_created = first_version.revision.date_created
        second_version_created = second_version.revision.date_created

        if first_version_created > second_version_created:
            # If the first version is after the second version
            later_version = first_version
            earlier_version = second_version
        else:
            # The first version is before the second version
            later_version = second_version
            earlier_version = first_version

        return json.loads(earlier_version.serialized_data), json.loads(later_version.serialized_data)

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)

        self.context['activetab'] = 'history'
        self.context['hide_item_actions'] = True

        self.concept = self.get_item(self.request.user)
        self.model = self.get_model(self.concept)

        version_1 = self.request.GET.get('v1')
        version_2 = self.request.GET.get('v2')

        if not version_1 or not version_2:
            self.context['not_all_versions_selected'] = True
            return self.context

        first_version = reversion.models.Version.objects.get(pk=version_1)
        second_version = reversion.models.Version.objects.get(pk=version_2)
        version_permission_1 = VersionPermissions.objects.get_object_or_none(pk=version_1)
        version_permission_2 = VersionPermissions.objects.get_object_or_none(pk=version_2)

        if not self.user_can_view_version(self.concept, version_permission_1) and self.user_can_view_version(
                self.concept, version_permission_2):
            raise PermissionDenied

        # Need to pass this context to rebuild query parameters in template
        self.context['version_1_id'] = version_1
        self.context['version_2_id'] = version_2

        try:
            earlier_json, later_json = self.get_version_jsons(first_version, second_version)
        except json.JSONDecodeError:
            self.context['cannot_compare'] = True
            return self.context

        raw = self.request.GET.get('raw')
        if raw:
            self.context['raw'] = True
            self.context['diffs'] = self.generate_diff(earlier_json, later_json, raw=True)
        else:
            self.context['diffs'] = self.generate_diff(earlier_json, later_json)

        return self.context


class ConceptVersionListView(SimpleItemGet, VersionsMixin, ListView):
    """
    View  that lists all the specific versions of a particular concept
    """
    template_name = 'aristotle_mdr/compare/versions.html'
    item_action_url = 'aristotle:item_version'

    def get_object(self):
        return self.get_item(self.request.user).item  # Versions are now saved on the model rather than the concept

    def get_queryset(self) -> List[Dict]:
        """Return a queryset of all the versions the user has permission to access as well as associated metadata
         involved in template rendering"""
        metadata_item = self.get_object()
        versions = self.get_versions(metadata_item)

        version_list = []
        version_to_permission = VersionPermissions.objects.in_bulk(versions)
        for version in versions:
            if version.id in version_to_permission:
                version_permission = version_to_permission[version.id]
                if version_permission is None:
                    # Default to displaying workgroup level permissions
                    version_permission_code = VISIBILITY_PERMISSION_CHOICES.workgroup
                else:
                    version_permission_code = version_permission.visibility
            else:
                version_permission_code = VISIBILITY_PERMISSION_CHOICES.workgroup

            version_list.append({
                'permission': int(version_permission_code),
                'version': version,
                'revision': version.revision,
                'url': reverse(self.item_action_url, args=[version.id])
            })

        return version_list

    def get_context_data(self, **kwargs) -> Dict:
        # Determine the editing permissions of the user
        metadata_item = self.get_object()
        USER_CAN_EDIT = user_can_edit(self.request.user, metadata_item)

        context = {'activetab': 'history',
                   'user_can_edit': USER_CAN_EDIT,
                   'object': self.get_object(),
                   'item': self.get_object(),
                   'versions': self.get_queryset(),
                   'choices': VISIBILITY_PERMISSION_CHOICES,
                   "hide_item_actions": True}

        return context


class CompareHTMLFieldsView(SimpleItemGet, VersionsMixin, TemplateView):
    """ A view to render two HTML fields side by side so that they can be compared visually"""
    template_name = 'aristotle_mdr/compare/rendered_field_comparision.html'

    def get_versions(self, version1, version2) -> Tuple:
        return (get_object_or_404(reversion.models.Version, pk=version1),
                get_object_or_404(reversion.models.Version, pk=version2))

    def get_object(self):
        return self.get_item(self.request.user).item  # Versions are now saved on the model rather than the concept

    def get_html_fields(self, version_1, version_2, field_query) -> List[str]:
        """Cleans and returns the content for the two versions of a HTML field """
        html_values = []
        fields = tuple(field_query.split('.'))

        versions = [json.loads(version_1.serialized_data),
                    json.loads(version_2.serialized_data)]
        for version in versions:
            version_data = version
            logger.debug("VERSION DATA" +  str(version_data))
            for field in fields:
                if version_data is None:
                    pass
                # Dynamically traverse data structure
                if isinstance(version_data, dict):
                    if field in version_data:
                        version_data = version_data[field]
                    else:
                        version_data = None

                elif isinstance(version_data, list):
                    try:
                        version_data = version_data[int(field)]
                    except IndexError:
                        version_data = None
            html_values.append(version_data)

        return html_values

    def apply_permission_checking(self, version_permission_1, version_permission_2):
        if not (self.user_can_view_version(self.metadata_item, version_permission_1) and self.user_can_view_version(
                self.metadata_item, version_permission_2)):
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        self.metadata_item = self.get_item(self.request.user).item

        context = {'activetab': 'history',
                   'hide_item_actions': True,
                   'item': self.get_object()}

        version_1 = self.request.GET.get('v1', None)
        version_2 = self.request.GET.get('v2', None)

        if not version_1 or not version_2:
            context['not_all_versions_selected'] = True
            return context

        first_version, second_version = self.get_versions(version_1, version_2)

        version_permission_1 = VersionPermissions.objects.get_object_or_none(pk=version_1)
        version_permission_2 = VersionPermissions.objects.get_object_or_none(pk=version_2)

        self.apply_permission_checking(version_permission_1, version_permission_2)

        field_query = self.request.GET.get('field')
        context['html_fields'] = self.get_html_fields(first_version, second_version, field_query)

        return context
