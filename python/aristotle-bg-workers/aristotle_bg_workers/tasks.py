from typing import Optional, List
import datetime
from io import StringIO

from django.core.management import call_command

from celery import shared_task, Task
from celery.utils.log import get_task_logger

from aristotle_mdr.utils.download import get_download_class

logger = get_task_logger(__name__)


def run_django_command(cmd, *args, **kwargs):
    err = StringIO()
    out = StringIO()
    call_command(cmd, stdout=out, stderr=err, **kwargs)
    err.seek(0)
    out.seek(0)
    message = 'Result:\n\n{out}\n\n{err}'.format(
        err=str(err.read()) or "None",
        out=str(out.read())
    )
    logger.debug(message)
    return message


class AristotleTask(Task):
    def update_state(self, task_id=None, state=None, meta=None):
        if task_id is None:
            task_id = self.request.id
        self.backend.store_result(task_id, meta, state=state, request=self.request)


@shared_task(base=AristotleTask, bind=True, name='long__reindex')
def reindex_task(self, *args, **kwargs):
    meta = {"requester": kwargs['requester'], "start_date": datetime.datetime.now()}
    self.update_state(meta=meta, state="STARTED")
    meta.update({"result": run_django_command('rebuild_index', interactive=False)})
    return meta


@shared_task(base=AristotleTask, bind=True, name='long__load_help')
def loadhelp_task(*args, **kwargs):
    meta = {"requester": kwargs['requester'], "start_date": datetime.datetime.now()}
    self.update_state(meta=meta, state="STARTED")
    meta.update({"result": run_django_command('load_aristotle_help')})
    return meta


@shared_task(name='fire_async_signal')
def fire_async_signal(namespace, signal_name, message = {}):
    from django.utils.module_loading import import_string
    import_string("%s.%s" % (namespace, signal_name))(message)


@shared_task(name='update_search_index')
def update_search_index(action, sender, instance, **kwargs):
    from django.apps import apps
    sender = apps.get_model(sender['app_label'], sender['model_name'])
    instance = apps.get_model(instance['app_label'], instance['model_name']).objects.filter(pk=instance['pk']).first()
    processor = apps.get_app_config('haystack').signal_processor
    if action == "save":
        logger.debug("UPDATING INDEX FOR {}".format(instance))
        processor.handle_save(sender, instance, **kwargs)
    elif action == "delete":
        processor.handle_delete(sender, instance, **kwargs)


@shared_task(name='download')
def download(download_type: str, item_ids: List[int], user_id: int, options={}) -> Optional[str]:
    dl_class = get_download_class(download_type)

    if dl_class is not None:
        # Instanciate downloader class
        downloader = dl_class(item_ids, user_id, options)
        # Get file url
        return downloader.download()

    return None
