from typing import Optional
from django.db.models import Model
from django.apps import apps
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


def fire(signal_name, obj=None, namespace="aristotle_mdr.contrib.async_signals", **kwargs):
    from django.utils.module_loading import import_string
    message = kwargs
    if getattr(settings, 'ARISTOTLE_ASYNC_SIGNALS', False):
        # pragma: no cover -- We've dropped channels, and are awaiting (pun) on celery stuff
        message.update({
            '__object__': {
                'pk': obj.pk,
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.model_name,
            },
            # "__signal__": signal_name,
        })
        from aristotle_bg_workers.celery import app
        message = clean_signal(message)
        app.send_task(
            'fire_async_signal',
            args=[namespace, signal_name],
            kwargs={"message": message}
        )

        # Channel("aristotle_mdr.contrib.channels.%s" % signal_name).send(message)
    else:
        message.update({'__object__': {'object': obj}})
        import_string("%s.%s" % (namespace, signal_name))(message)


def safe_object(message) -> Optional[Model]:
    __object__ = message['__object__']
    if __object__.get('object', None):
        instance = __object__['object']
    else:
        model = apps.get_model(__object__['app_label'], __object__['model_name'])
        instance = model.objects.filter(pk=__object__['pk']).first()
    return instance


def clean_signal(message):
    message.pop('signal', None)
    if message.get('changed_fields', False):
        message['changed_fields'] = list(message['changed_fields'])
    return message
