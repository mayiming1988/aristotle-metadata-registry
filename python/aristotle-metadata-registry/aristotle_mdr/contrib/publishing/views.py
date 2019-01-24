from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from aristotle_mdr.contrib.generic.views import GenericWithItemURLFormView
from aristotle_mdr.views.utils import CreateUpdateView

from .forms import PublicationForm, VersionPublicationForm
from .models import VersionPublicationRecord, PublicationRecord

import logging
logger = logging.getLogger(__name__)


def can_publish(user, item):
    return user.is_superuser or user == item.submitter


class VersionPublishMetadataFormView(GenericWithItemURLFormView):
    permission_checks = [can_publish]
    template_name = "aristotle_mdr/publish/publish_metadata_versions.html"
    form_class = PublicationForm

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()

        VersionPublicationRecord.objects.get_or_create(
            # content_object=self.item,
            content_type = ContentType.objects.get_for_model(self.item),
            object_id = self.item.pk
        )
        kwargs.update({'instance': self.item.version_publication_details.first()})
        return kwargs

    def form_valid(self, form):
        defaults={
            'public_user_publication_date': form.cleaned_data['public_user_publication_date'],
            'authenticated_user_publication_date': form.cleaned_data['authenticated_user_publication_date']
        }
        rec, c = VersionPublicationRecord.objects.update_or_create(
            content_type = ContentType.objects.get_for_model(self.item),
            object_id = self.item.pk,
            # user=self.request.user,
            defaults=defaults
        )
        return HttpResponseRedirect(self.get_success_url())


class PublishContentFormView(CreateUpdateView):
    template_name = "aristotle_mdr/publish/publish_object.html"
    model = PublicationRecord
    fields = ['permission', 'publication_date']

    content_type = None
    publishable_object = None

    def get_content_type(self):
        if not self.content_type:
            model_name = self.kwargs['model_name']
            if model_name in ["concept", "metadata"]:
                model_name = "_concept"
            self.content_type = get_object_or_404(ContentType, model=model_name)
        return self.content_type

    def get_publishable_object(self):
        if not self.publishable_object:
            content_type = self.get_content_type()
            model = content_type.model_class()
    
            if not getattr(model, 'publication_details', None):
                raise Http404
            # Verify the thing we want to publish exists
            self.publishable_object = get_object_or_404(model, pk=self.kwargs['iid'])
            self.publishable_object = getattr(self.publishable_object, "item", self.publishable_object)

        return self.publishable_object

    def get_object(self, queryset=None):

        content_type = self.get_content_type()
        publishable_object = self.get_publishable_object()

        return PublicationRecord.objects.filter(content_type=content_type, object_id=self.kwargs['iid']).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "item": self.get_publishable_object()
        })
        return context
    
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.content_type = self.get_content_type()
        self.object.object_id = self.get_publishable_object().pk
        self.object.publisher = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        published_object = self.get_publishable_object()
        message = _(
            'Object "%(object_name)s" successfully published, '
            'it will be visible to %(user_type)s '
            'from %(date)s'
        ) % {
            'object_name': published_object.name,
            'date': self.object.publication_date,
            'user_type': self.object.get_permission_display(),
        }
        messages.add_message(self.request, messages.INFO, message)

        return self.get_publishable_object().get_absolute_url()
    
