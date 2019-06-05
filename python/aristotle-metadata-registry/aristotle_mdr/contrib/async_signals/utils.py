from django.apps import apps
from django.conf import settings
from django.db.models import Model
from django.utils.module_loading import import_string
from typing import Optional, Dict

from aristotle_bg_workers.utils import run_task_by_name_on_commit, lookup_model


def fire(signal_name, obj=None, namespace="aristotle_mdr.contrib.async_signals", **kwargs):
    """Starts celery task to run given signal code"""
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
        run_task_by_name_on_commit('fire_async_signal', args=[namespace, signal_name], kwargs={'message': message})
    else:
        message.update({'__object__': {'object': obj}})
        import_string("%s.%s" % (namespace, signal_name))(message)


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
