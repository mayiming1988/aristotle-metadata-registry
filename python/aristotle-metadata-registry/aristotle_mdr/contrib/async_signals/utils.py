from django.conf import settings
from django.db.models import Model
from django.utils.module_loading import import_string
from typing import Dict

from aristotle_bg_workers.utils import run_task_by_name_on_commit, lookup_model

import logging
logger = logging.getLogger(__name__)


def fire(signal_name, obj=None, namespace="aristotle_mdr.contrib.async_signals", **kwargs):
    """Starts celery task to run given signal code"""

    if getattr(settings, 'ARISTOTLE_ASYNC_SIGNALS', False):
        # Add object data to message
        kwargs.update({
            '__object__': {
                'pk': obj.pk,
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.model_name,
            },
        })
        kwargs = clean_signal(kwargs)  # Clean message of unwanted (and unserializable) content

        # Run the task after database commit:
        run_task_by_name_on_commit('fire_async_signal', args=[namespace, signal_name], kwargs={'message': kwargs})
    else:
        kwargs.update({'__object__': {'object': obj}})
        import_string("%s.%s" % (namespace, signal_name))(kwargs)


def safe_object(message) -> Model:
    """Fetch an object from its __object__ data"""
    objdata = message['__object__']
    # If we have the actual object use that
    if 'object' in objdata:
        return objdata['object']
    # Fetch object by app_label model_name and pk
    model = lookup_model(objdata)
    # This will result in an exception if the object is not found
    # If uncaught the task will fail which is usually fine, since failing early gives a more useful error
    return model.objects.get(pk=objdata['pk'])


def clean_signal(kwargs: Dict):
    """Clean signal kwargs before serialization"""
    # Remove these keys from mapping
    # These are described here https://docs.djangoproject.com/en/dev/ref/signals/
    keys_to_remove = ('signal', 'model', 'pk_set')
    for key in keys_to_remove:
        if key in kwargs:
            del kwargs[key]

    # Switch changed_fields to a list
    if 'changed_fields' in kwargs:
        kwargs['changed_fields'] = list(kwargs['changed_fields'])

    return kwargs
