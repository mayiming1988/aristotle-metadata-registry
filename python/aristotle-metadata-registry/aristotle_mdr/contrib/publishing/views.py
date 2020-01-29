from braces.views import PermissionRequiredMixin

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from aristotle_mdr.views.utils import CreateUpdateView
from aristotle_mdr import perms

from .models import PublicationRecord

import logging
logger = logging.getLogger(__name__)


class PublishContentBaseView(PermissionRequiredMixin, CreateUpdateView):
    template_name = "aristotle_mdr/publish/publish_object.html"
    model = PublicationRecord
    fields = ['permission', 'publication_date']
    raise_exception = True
    redirect_unauthenticated_users = True

    content_type = None
    publishable_object = None

    def check_permissions(self, request):
        publishable_object = self.get_publishable_object()
        return perms.user_can_publish_object(request.user, publishable_object)

    def get_content_type(self):
        if not self.content_type:
            model_name = self.kwargs['model_name']
            self.content_type = get_object_or_404(ContentType, model=model_name)
            if getattr(self.content_type.model_class(), "model_to_publish", None):
                model = self.content_type.model_class().model_to_publish().__name__.lower()
                self.content_type = get_object_or_404(ContentType, model=model)
        return self.content_type

    def get_publishable_object(self):
        if not self.publishable_object:
            content_type = self.get_content_type()
            model = content_type.model_class()

            if not getattr(model, 'publication_details', None):
                raise Http404

            # Verify the thing we want to publish exists
            self.publishable_object = get_object_or_404(model, pk=self.kwargs['iid'])
            # self.publishable_object = getattr(self.publishable_object, "item", self.publishable_object)

        return self.publishable_object

    def get_object(self, queryset=None):

        content_type = self.get_content_type()
        publishable_object = self.get_publishable_object()

        return PublicationRecord.objects.filter(content_type=content_type, object_id=self.kwargs['iid']).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "item": self.get_publishable_object(),
            "submit_url": self.request.get_full_path()
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
            'object_name': str(published_object),
            'date': self.object.publication_date,
            'user_type': self.object.get_permission_display(),
        }
        messages.add_message(self.request, messages.INFO, message)

        return self.get_publishable_object().get_absolute_url()


class PublishRegistryContentFormView(PublishContentBaseView):
    def check_permissions(self, request):
        publishable_object = self.get_publishable_object()
        return request.user.is_superuser


class PublishContentFormView(PublishContentBaseView):

    def dispatch(self, request, *args, **kwargs):
        publishable_object = self.get_publishable_object()
        if not publishable_object.stewardship_organisation:
            from django.shortcuts import render_to_response
            return render_to_response(
                "aristotle_mdr/publish/errors/no_steward.html",
                {"item": publishable_object},
                status=404
            )
        return super().dispatch(request, *args, **kwargs)
