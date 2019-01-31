from django import forms
from django.db.models import DateField
from django.forms.models import BaseModelFormSet, BaseInlineFormSet
from django.forms.formsets import BaseFormSet
from django.forms.models import modelformset_factory

from aristotle_mdr.models import _concept, AbstractValue, ValueDomain, ValueMeaning
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker

from django_bulk_update.helper import bulk_update


import logging
logger = logging.getLogger(__name__)

datePickerOptions = {
    "format": "YYYY-MM-DD",
    "useCurrent": False,
    "widgetPositioning": {
        "horizontal": "left",
        "vertical": "bottom"
    }
}


class HiddenOrderMixin(object):
    is_ordered = True

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["ORDER"].widget = forms.HiddenInput()


class HiddenOrderFormset(HiddenOrderMixin, BaseFormSet):
    pass


class HiddenOrderModelFormSet(HiddenOrderMixin, BaseModelFormSet):

    def save_new(self, form, commit=True):
        inst = form.save(commit=False)
        setattr(inst, self.ordering_field, form.cleaned_data['ORDER'])
        if commit:
            inst.save()
        return inst

    def save_existing(self, form, instance, commit=True):
        return self.save_new(form, commit)


class HiddenOrderInlineFormset(HiddenOrderMixin, BaseInlineFormSet):
    def save(self, commit=True):
        super().save(commit=False)
        # Save formset so we have access to deleted_objects and save_m2m

        for form in self.ordered_forms:
            # Loop through the forms so we can add the order value to the ordering field
            # ordered_forms does not contain forms marked for deletion
            obj = form.save(commit=False)
            # setattr(obj, model_to_add_field, item)
            setattr(obj, self.ordering_field, form.cleaned_data['ORDER'])
            obj.save()

        for obj in self.deleted_objects:
            # Delete objects marked for deletion
            obj.delete()

        # Save any m2m relations on the ojects (not actually needed yet)
        self.save_m2m()


# Below are some util functions for creating o2m and m2m querysets
# They are used in the generic alter views and the ExtraFormsetMixin


def one_to_many_formset_excludes(item, model_to_add):
    # creates a list of extra fields to be excluded based on the item related to the weak entity
    extra_excludes = []
    if isinstance(item, ValueDomain):
        # Value Domain specific excludes
        if issubclass(model_to_add, AbstractValue):
            if not item.conceptual_domain:
                extra_excludes.append('value_meaning')
            else:
                extra_excludes.append('meaning')

    return extra_excludes


def one_to_many_formset_filters(formset, item):
    # applies different querysets to the forms after they are instanciated
    if isinstance(item, ValueDomain) and item.conceptual_domain:
        # Only show value meanings from this items conceptual domain
        vmqueryset = ValueMeaning.objects.filter(conceptual_domain=item.conceptual_domain)

        for form in formset:
            if issubclass(form._meta.model, AbstractValue):
                form.fields['value_meaning'].queryset = vmqueryset

    return formset


def get_aristotle_widgets(model, ordering_field=None):

    _widgets = {}

    for f in model._meta.fields:
        foreign_model = model._meta.get_field(f.name).related_model
        if foreign_model and issubclass(foreign_model, _concept):
            _widgets.update({
                f.name: widgets.ConceptAutocompleteSelect(
                    model=foreign_model
                )
            })

        if isinstance(model._meta.get_field(f.name), DateField):
            _widgets.update({
                f.name: BootstrapDateTimePicker(options=datePickerOptions)
            })

        if ordering_field is not None and f.name == ordering_field:
            _widgets.update({
                ordering_field: forms.HiddenInput()
            })

    for f in model._meta.many_to_many:
        foreign_model = model._meta.get_field(f.name).related_model
        if foreign_model and issubclass(foreign_model, _concept):
            _widgets.update({
                f.name: widgets.ConceptAutocompleteSelectMultiple(
                    model=foreign_model
                )
            })

    return _widgets


def ordered_formset_factory(model, ordering_field, exclude=[]):
    # Formset factory for a hidden order model formset with aristotle widgets
    _widgets = get_aristotle_widgets(model)

    formset = modelformset_factory(
        model,
        formset=HiddenOrderModelFormSet,
        can_order=True,  # we assign this back to the ordering field
        can_delete=True,
        exclude=exclude,
        extra=0,
        widgets=_widgets
    )
    formset.ordering_field = ordering_field
    return formset


def ordered_formset_save(formset, item, model_to_add_field, ordering_field):
    # Save a formset created with the above factory

    item.save()  # do this to ensure we are saving reversion records for the item, not just the values
    formset.save(commit=False)  # Save formset so we have access to deleted_objects and save_m2m

    new = []
    for obj in formset.new_objects:
        # Loop through the forms so we can add the order value to the ordering field
        # ordered_forms does not contain forms marked for deletion
        setattr(obj, model_to_add_field, item)
        new.append(obj)

    if new:
        formset.model.objects.bulk_create(new)

    changed = []
    for record in formset.changed_objects:
        # record is a tuple with obj and form changed_data
        obj = record[0]
        setattr(obj, model_to_add_field, item)
        changed.append(obj)

    if changed:
        bulk_update(changed, batch_size=500)

    if formset.deleted_objects:
        formset.models.objects.bulk_delete(formset.deleted_objects)

    # Save any m2m relations on the ojects (not actually needed yet)
    formset.save_m2m()
