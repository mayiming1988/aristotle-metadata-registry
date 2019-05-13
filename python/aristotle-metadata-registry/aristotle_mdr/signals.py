from django.conf import settings
from django.db.models.signals import m2m_changed, post_save, pre_delete
# from reversion.signals import post_revision_commit
import haystack.signals as signals  # .RealtimeSignalProcessor as RealtimeSignalProcessor
from aristotle_mdr.utils import fetch_metadata_apps
# Don't import aristotle_mdr.models directly, only pull in whats required,
#  otherwise Haystack gets into a circular dependancy.

# class AristotleSignalProcessor(signals.BaseSignalProcessor):
# Replace below with this when doing a dataload (shuts off Haystack)
#    pass

import logging
logger = logging.getLogger(__name__)


# @receiver(pre_save)
def pre_save_clean(sender, instance, *args, **kwargs):
    instance.full_clean()


class AristotleSignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
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
        logger.critical("HELLO WORLDDDDD")
        instance = concept.item
        self.async_handle_save(instance.__class__, instance)

    # Called on the saving of all objects
    def handle_object_save(self, sender, instance, **kwargs):
        from aristotle_mdr.models import _concept, aristotleComponent
        if isinstance(instance, _concept) and type(instance) is not _concept:
            if instance._meta.app_label in fetch_metadata_apps():
                obj = instance.item
                self.async_handle_save(obj.__class__, obj, **kwargs)
            else:
                return

        from aristotle_mdr.models import DiscussionPost
        if isinstance(instance, DiscussionPost):
            self.async_handle_save(type(instance), instance, **kwargs)

        # Components should have parents, but lets be kind.
        if issubclass(sender, aristotleComponent) and hasattr(instance, "parentItem"):
            obj = instance.parentItem.item
            self.async_handle_save(obj.__class__, obj, **kwargs)

    def handle_concept_delete(self, sender, instance, **kwargs):
        # Delete index *before* the object, as we need to query it to check the actual subclass.
        obj = instance.item
        self.async_handle_delete(obj.__class__, obj, **kwargs)

    def update_visibility_review_request(self, sender, instance, **kwargs):
        from aristotle_mdr.contrib.reviews.models import ReviewRequest
        assert(sender in [ReviewRequest, ReviewRequest.concepts.through])
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
            super().handle_save(sender, instance, **kwargs)   # Call haystack handle save
        else:
            from aristotle_mdr.contrib.async_signals.utils import clean_signal
            message = clean_signal(kwargs)
            # TODO: Find out why the model k-argument is showing up now.
            message.pop('model', None)
            # TODO: I JUST FOUND ANOTHER ERROR: THE TYPE OF THE PK ATTRIBUTE IS A SET TYPE AND IT IS NOT SERIALIZABLE.
            message.pop('pk_set', None)

            from aristotle_bg_workers.celery import app
            app.send_task(
                'update_search_index',
                args=[
                    'save',
                    {   # sender
                        'app_label': sender._meta.app_label,
                        'model_name': sender._meta.model_name,
                    },
                    {   # instance
                        'pk': instance.pk,
                        'app_label': instance._meta.app_label,
                        'model_name': instance._meta.model_name,
                    },
                ],
                kwargs=message
            )

    def async_handle_delete(self, sender, instance, **kwargs):
        if not settings.ARISTOTLE_ASYNC_SIGNALS:
            super().handle_delete(sender, instance, **kwargs)
        else:
            from aristotle_bg_workers.celery import app
            app.send_task(
                'update_search_index',
                args=[
                    'delete',
                    {   # sender
                        'app_label': sender._meta.app_label,
                        'model_name': sender._meta.model_name,
                    },
                    {   # instance
                        'pk': instance.pk,
                        'app_label': instance._meta.app_label,
                        'model_name': instance._meta.model_name,
                    },
                ],
                kwargs=kwargs
            )
