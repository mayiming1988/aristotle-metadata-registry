from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, pre_delete
from haystack import signals as haystack_signals

from aristotle_mdr.contrib.async_signals.utils import clean_signal
from aristotle_bg_workers.tasks import update_search_index, delete_search_index
from aristotle_bg_workers.utils import run_task_on_commit
from aristotle_mdr.utils import fetch_metadata_apps

# Don't import aristotle_mdr.models directly, only pull in whats required,
#  otherwise Haystack gets into a circular dependancy.

import logging

logger = logging.getLogger(__name__)


# This is imported by other modules
def pre_save_clean(sender, instance, *args, **kwargs):
    instance.full_clean()


class AristotleSignalProcessor(haystack_signals.BaseSignalProcessor):
    def setup(self):
        """Connect django signals to this classes methods"""
        from aristotle_mdr.models import _concept, concept_visibility_updated
        from aristotle_mdr.contrib.reviews.models import ReviewRequest
        from aristotle_mdr.contrib.help.models import HelpPage, ConceptHelp
        from aristotle_mdr.contrib.publishing.models import PublicationRecord

        post_save.connect(self.handle_object_save)
        pre_delete.connect(self.handle_concept_delete, sender=_concept)
        post_save.connect(self.update_visibility_review_request, sender=ReviewRequest)
        m2m_changed.connect(self.update_visibility_review_request, sender=ReviewRequest.concepts.through)
        concept_visibility_updated.connect(self.handle_concept_recache)
        post_save.connect(self.async_handle_save, sender=HelpPage)
        post_save.connect(self.async_handle_save, sender=ConceptHelp)
        post_save.connect(self.item_published, sender=PublicationRecord)
        super().setup()

    def teardown(self):  # pragma: no cover
        from aristotle_mdr.models import _concept
        post_save.disconnect(self.handle_object_save, sender=_concept)
        # post_revision_commit.disconnect(self.handle_concept_revision)
        pre_delete.disconnect(self.handle_concept_delete, sender=_concept)
        super().teardown()

    def handle_concept_recache(self, concept, **kwargs):
        instance = concept.item
        self.async_handle_save(instance.__class__, instance)

    # Called on the saving of all objects
    def handle_object_save(self, sender, instance, **kwargs):
        from aristotle_mdr.models import _concept, aristotleComponent

        itype = type(instance)

        # If saving a concept subclass
        if isinstance(instance, _concept) and itype is not _concept:
            if instance._meta.app_label in fetch_metadata_apps():
                # If newly created
                if kwargs.get('created', False):
                    # Make sure we have a _concept_ptr
                    if hasattr(instance, '_concept_ptr'):
                        concept = instance._concept_ptr
                        ct = ContentType.objects.get_for_model(itype)
                        concept._type = ct
                        concept.save()

                # Handle async
                obj = instance.item
                self.async_handle_save(obj.__class__, obj, **kwargs)

        from aristotle_mdr.models import DiscussionPost
        if isinstance(instance, DiscussionPost):
            self.async_handle_save(type(instance), instance, **kwargs)

        # Components should have parents, but lets be kind.
        if issubclass(sender, aristotleComponent):
            parent_item = instance.parentItem
            if parent_item is not None:
                obj = parent_item.item
                self.async_handle_save(obj.__class__, obj, **kwargs)

    def handle_concept_delete(self, sender, instance, **kwargs):
        # Delete index *before* the object, as we need to query it to check the actual subclass.
        obj = instance.item
        self.async_handle_delete(obj.__class__, obj, **kwargs)

    def update_visibility_review_request(self, sender, instance, **kwargs):
        from aristotle_mdr.contrib.reviews.models import ReviewRequest
        assert (sender in [ReviewRequest, ReviewRequest.concepts.through])
        for concept in instance.concepts.all():
            obj = concept.item
            self.async_handle_save(obj.__class__, obj, **kwargs)

    def item_published(self, sender, instance, **kwargs):
        obj = instance.content_object
        from aristotle_mdr.models import _concept
        if not issubclass(obj.__class__, _concept):
            return
        obj = obj.item
        self.async_handle_save(obj.__class__, obj, **kwargs)

    def async_handle_save(self, sender, instance, **kwargs):
        # Dev tests settings
        if not settings.ARISTOTLE_ASYNC_SIGNALS:
            super().handle_save(sender, instance, **kwargs)  # Call haystack handle save
        else:
            message = clean_signal(kwargs)

            task_args = [
                {  # sender
                    'app_label': sender._meta.app_label,
                    'model_name': sender._meta.model_name,
                },
                {  # instance
                    'pk': instance.pk,
                    'app_label': instance._meta.app_label,
                    'model_name': instance._meta.model_name,
                },
            ]

            # Start task on commit
            run_task_on_commit(update_search_index, args=task_args, kwargs=message)

    def async_handle_delete(self, sender, instance, **kwargs):
        if not settings.ARISTOTLE_ASYNC_SIGNALS:
            super().handle_delete(sender, instance, **kwargs)
        else:
            message = clean_signal(kwargs)
            args = [
                {  # sender
                    'app_label': sender._meta.app_label,
                    'model_name': sender._meta.model_name,
                },
                {  # instance
                    'pk': instance.pk,
                    'app_label': instance._meta.app_label,
                    'model_name': instance._meta.model_name
                },
            ]
            delete_search_index.delay(*args, **message)
