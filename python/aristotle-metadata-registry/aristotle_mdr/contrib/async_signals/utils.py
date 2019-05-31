from typing import Optional, Mapping
from django.db.models import Model
from django.apps import apps
from django.conf import settings

from aristotle_bg_workers.tasks import fire_async_signal
from aristotle_bg_workers.utils import run_task_on_commit
import logging
logger = logging.getLogger(__name__)


def fire(signal_name, obj=None, namespace="aristotle_mdr.contrib.async_signals", **kwargs):
    """Starts celery task to run given signal code"""
    from django.utils.module_loading import import_string
    message = kwargs
    if getattr(settings, 'ARISTOTLE_ASYNC_SIGNALS', False):
        # pragma: no cover -- We've dropped channels, and are awaiting (pun) on celery stuff

        # Add object data to message
        message.update({
            '__object__': {
                'pk': obj.pk,
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.model_name,
            },
        })
        # Clean message of unwanted (and unserializable) content
        message = clean_signal(message)
        # Run the task after database commit
        run_task_on_commit(fire_async_signal, args=[namespace, signal_name], kwargs={'message': message})
    else:
        message.update({'__object__': {'object': obj}})
        import_string("%s.%s" % (namespace, signal_name))(message)


def safe_object(message) -> Optional[Model]:
    """Fetch an object from its __object__ data"""
    objdata = message['__object__']
    # If we have the actual object use that
    if 'object' in objdata:
        return objdata['object']
    # Fetch object by app_label model_name and pk
    model = apps.get_model(objdata['app_label'], objdata['model_name'])
    return model.objects.filter(pk=objdata['pk']).first()


def clean_signal(kwargs: Mapping):
    """Clean signal kwargs before serialization"""
    # Remove these keys from mapping
    keys_to_remove = ('signal', 'model', 'pk_set')
    for key in keys_to_remove:
        if key in kwargs:
            del kwargs[key]

    # Switch changed_fields to a list
    if 'changed_fields' in kwargs:
        kwargs['changed_fields'] = list(kwargs['changed_fields'])

    return kwargs
