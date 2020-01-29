import reversion
import aristotle_mdr.models as MDR
import aristotle_mdr.contrib.favourites.models as fav_models
from typing import Any
from django import forms
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import HiddenInput
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from aristotle_mdr.forms import ChangeStatusForm, CASCADE_HELP_TEXT, CASCADE_OPTIONS_PLURAL
from aristotle_mdr.forms.fields import ForbiddenAllowedModelMultipleChoiceField
from aristotle_mdr.perms import (
    user_can_view,
    user_is_registrar,
    user_can_move_any_workgroup,
    user_can_move_any_stewardship_organisation,
    user_can_remove_from_stewardship_organisation,
    user_can_move_to_stewardship_organisation
)
from aristotle_mdr.forms.creation_wizards import UserAwareForm
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.utils import fetch_aristotle_downloaders


class BulkActionForm(UserAwareForm):
    items_help_text = ""  # Override this attribute to provide the items help text to the template.
    classes = ""
    redirect: bool = False
    confirm_page: Any = None
    all_in_queryset = forms.BooleanField(
        label=_("All items"),
        required=False,
        widget=HiddenInput()
    )
    qs = forms.CharField(
        label=_("All items"),
        required=False,
        widget=HiddenInput()
    )

    def __init__(self, form, *args, **kwargs):
        self.initial_items = kwargs.pop('items', [])

        self.request = kwargs.pop('request')
        if 'user' in kwargs.keys():
            self.user = kwargs.get('user', None)
            queryset = MDR._concept.objects.visible(self.user)
        else:
            queryset = MDR._concept.objects.public()

        if 'data' not in kwargs:
            super().__init__(form, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)

        self.fields['items'] = ForbiddenAllowedModelMultipleChoiceField(
            label="Items",
            help_text=self.items_help_text,
            queryset=queryset,
            validate_queryset=MDR._concept.objects.all(),
            required=False,
            initial=self.initial_items,
            widget=widgets.ConceptAutocompleteSelectMultiple()
        )

    @property
    def items_to_change(self):
        if bool(self.cleaned_data.get('all_in_queryset', False)):
            filters = {}
            from aristotle_mdr.utils.cached_querysets import get_queryset_from_uuid
            items = get_queryset_from_uuid(self.cleaned_data.get('qs', ""), MDR._concept)

            _slice = {"low": items.query.low_mark, "high": items.query.high_mark}
            items.query.low_mark = 0
            items.query.high_mark = None
            items = items.filter(**filters).visible(self.user)
            items.query.set_limits(**_slice)
        else:
            items = self.cleaned_data.get('items')
        return items

    @classmethod
    def can_use(cls, user):
        return True

    @classmethod
    def text(cls):
        if hasattr(cls, 'action_text'):
            return cls.action_text
        from django.utils.text import camel_case_to_spaces
        txt = cls.__name__
        txt = txt.replace('Form', '')
        txt = camel_case_to_spaces(txt)
        return txt


class LoggedInBulkActionForm(BulkActionForm):
    @classmethod
    def can_use(cls, user):
        return user.is_active


class AddFavouriteForm(LoggedInBulkActionForm):
    classes = "fa-bookmark"
    action_text = _('Add favourite')

    def make_changes(self):
        items = self.items_to_change
        items = items.visible(self.user)

        fav_tag, created = fav_models.Tag.objects.get_or_create(
            profile=self.user.profile,
            primary=True,
        )

        num_items = 0
        bad_items = []
        for item in items:
            if not user_can_view(self.user, item):
                bad_items.append(str(item.id))
            else:
                favourite, created = fav_models.Favourite.objects.get_or_create(
                    tag=fav_tag,
                    item=item
                )
                if created:
                    num_items += 1

        message_text = "{} items favourited.".format(num_items)
        return _(message_text)


class RemoveFavouriteForm(LoggedInBulkActionForm):
    classes = "fa-minus-square"
    action_text = _('Remove favourite')

    def make_changes(self):
        items = self.items_to_change
        favourites = fav_models.Favourite.objects.filter(
            tag__primary=True,
            tag__profile=self.user.profile,
            item__in=list(items)
        )
        favourites.delete()
        return '%(num_items)s items removed from favourites.' % {'num_items': favourites.count()}


class ChangeStateForm(ChangeStatusForm, BulkActionForm):
    confirm_page = "aristotle_mdr/actions/bulk_actions/change_status.html"
    classes = "fa-university"
    action_text = _('Change registration status')
    items_help_text = "These are the items that will be registered. Add or remove additional items with the " \
                      "autocomplete box."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cascadeRegistration'].label = "Cascade endorsement"

    cascadeRegistration = forms.ChoiceField(
        initial=0,
        choices=CASCADE_OPTIONS_PLURAL,
        help_text=CASCADE_HELP_TEXT,
        widget=forms.RadioSelect(),
    )

    @classmethod
    def can_use(cls, user):
        return user_is_registrar(user)


class BulkMoveMetadataMixin:
    org_type = ""  # Override this attribute with "workgroup" or "registration authority".

    def generate_moving_message(self, org_name, successfully_moved_items: int, failed_items=None) -> str:
        if not failed_items:
            message = _("%(num_items)s items moved into the %(org_type)s '%(new_wgs)s'.") % {
                'num_items': successfully_moved_items,
                'new_wgs': org_name,
                'org_type': self.org_type,
            }
        else:
            message = _(
                "%(num_items)s items moved into the %(org_type)s '%(new_wgs)s'. \n"
                "Some items failed, they had the id's: %(bad_ids)s"
            ) % {
                'num_items': successfully_moved_items,
                'new_wgs': org_name,
                'org_type': self.org_type,
                'bad_ids': ", ".join(failed_items),
            }
        return message


class ChangeWorkgroupForm(BulkActionForm, BulkMoveMetadataMixin):
    org_type = "workgroup"
    items_help_text = "These are the items that will be moved between workgroups. Add or remove additional items " \
                      "with the autocomplete box."
    confirm_page = "aristotle_mdr/actions/bulk_actions/change_workgroup.html"
    classes = "fa-users"
    action_text = _('Change workgroup')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['workgroup'] = forms.ModelChoiceField(
            label="Workgroup to move items to",
            queryset=self.user.profile.workgroups
        )
        self.fields['changeDetails'] = forms.CharField(
            label="Change notes (optional)",
            required=False,
            widget=forms.Textarea
        )

    def make_changes(self):
        import reversion
        from aristotle_mdr.perms import user_can_remove_from_workgroup, user_can_move_to_workgroup

        new_workgroup = self.cleaned_data['workgroup']
        items = self.cleaned_data['items']

        if not user_can_move_to_workgroup(self.user, new_workgroup):
            raise PermissionDenied

        move_from_checks = {}  # Cache workgroup permissions as we check them to speed things up.

        failed = []
        success = []
        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.user)
            for item in items:
                if item.workgroup:
                    can_move = move_from_checks.get(item.workgroup.pk, None)
                    if can_move is None:
                        can_move = user_can_remove_from_workgroup(self.user, item.workgroup)
                        move_from_checks[item.workgroup.pk] = can_move
                else:
                    can_move = True  # There is no workgroup, the user can move their own item.

                if not can_move:
                    failed.append(item)
                else:
                    success.append(item)
                    item.workgroup = new_workgroup
                    item.save()

            failed = list(set(failed))
            success = list(set(success))
            bad_items = sorted([str(i.id) for i in failed])

            return self.generate_moving_message(new_workgroup.name, len(success), failed_items=bad_items)

    @classmethod
    def can_use(cls, user):
        return user_can_move_any_workgroup(user)


class ChangeStewardshipOrganisationForm(BulkActionForm, BulkMoveMetadataMixin):
    org_type = "registration authority"
    items_help_text = "These are the items that will be moved to a new stewardship organisation. Add or remove " \
                      "additional items within the autocomplete box."
    confirm_page = "aristotle_mdr/actions/bulk_actions/change_stewardship_organisation.html"
    classes = "fa-sitemap"
    action_text = _("Change stewardship organisation")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['steward_org'] = forms.ModelChoiceField(
            label="Stewardship Organisation to move items to ",
            queryset=self.user.profile.stewardship_organisations,
            widget=forms.Select(attrs={'class': 'form-control'}),
        )

        self.fields['changeDetails'] = forms.CharField(
            label="Change notes (optional)",
            required=False,
            widget=forms.Textarea
        )

    def apply_move_permission_checking(self, item, move_from_checks) -> bool:

        if item.stewardship_organisation is None:
            can_move_permission = True  # If there is no org, the user can move their own item.
        else:
            can_move_permission = move_from_checks.get(item.stewardship_organisation.pk, None)
            if can_move_permission is None:
                can_move_permission = user_can_remove_from_stewardship_organisation(self.user,
                                                                                    item.stewardship_organisation)
                # Cache the can move permission
                move_from_checks[item.stewardship_organisation.pk] = can_move_permission

        return can_move_permission

    def make_changes(self):
        new_stewardship_org = self.cleaned_data['steward_org']
        # change_details = self.cleaned_data['changeDetails']
        items = self.cleaned_data['items']

        failed = []
        succeeded = []

        if not user_can_move_to_stewardship_organisation(self.user, new_stewardship_org):
            raise PermissionDenied

        move_from_checks = {}  # Cache some of the move from checks to speed up the view

        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.user)
            for item in items:
                can_move_permission = self.apply_move_permission_checking(item, move_from_checks)
                if not can_move_permission:
                    # There's no permission to move the item.
                    failed.append(item)
                else:
                    # There's permission, move the item.
                    succeeded.append(item)
                    item.workgroup = None
                    item.stewardship_organisation = new_stewardship_org
                    item.save()

            failed = list(set(failed))
            success = list(set(succeeded))
            failed_items = sorted([str(i.id) for i in failed])

            return self.generate_moving_message(new_stewardship_org.name, len(success), failed_items=failed_items)

    @classmethod
    def can_use(cls, user):
        return user_can_move_any_stewardship_organisation(user)


class DownloadActionForm(BulkActionForm):
    def make_changes(self):
        from aristotle_mdr.contrib.redirect.exceptions import Redirect
        items = self.items_to_change
        get_params = '?' + '&'.join(['items=%s' % i.id for i in items])
        url = reverse('aristotle:download_options', kwargs={'download_type': self.download_type}) + get_params
        raise Redirect(url=url)


class QuickPDFDownloadForm(DownloadActionForm):
    classes = "fa-file-pdf-o"
    action_text = _('Quick PDF download')
    items_label = "Items that are downloaded"
    download_type = 'pdf'
    title = None


class BulkDownloadForm(DownloadActionForm):
    items_help_text = "These are the items that will be downloaded"
    confirm_page = "aristotle_mdr/actions/bulk_actions/bulk_download.html"
    classes = "fa-download"
    action_text = _('Bulk download')

    download_type = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['download_type'] = forms.ChoiceField(
            choices=[
                (d_type.download_type, d_type.label)
                for d_type in fetch_aristotle_downloaders()
            ],
            widget=forms.RadioSelect
        )
        self.fields['items'].required = True

    def make_changes(self):
        self.download_type = self.cleaned_data['download_type']
        super().make_changes()
