from django.http import HttpResponseRedirect

from aristotle_mdr.contrib.generic.views import GenericWithItemURLFormView
from .forms import MetadataPublishForm
from .models import VersionPublicationRecord


def is_submitter_or_super(user, item):
    return user.is_superuser or user == item.submitter


class PublishMetadataFormView(GenericWithItemURLFormView):
    permission_checks = [is_submitter_or_super]
    template_name = "aristotle_mdr/publish/publish_metadata.html"
    form_class = MetadataPublishForm

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()

        VersionPublicationRecord.objects.get_or_create(
            concept=self.item,
        )
        kwargs.update({'instance': self.item.versionpublicationrecord})
        return kwargs

    def form_valid(self, form):
        defaults={
            'public_user_publication_date': form.cleaned_data['public_user_publication_date'],
            'authenticated_user_publication_date': form.cleaned_data['authenticated_user_publication_date']
        }
        rec, c = VersionPublicationRecord.objects.update_or_create(
            concept=self.item,
            # user=self.request.user,
            defaults=defaults
        )
        return HttpResponseRedirect(self.get_success_url())
