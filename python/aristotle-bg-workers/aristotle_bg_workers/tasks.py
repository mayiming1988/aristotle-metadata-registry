from typing import Optional, List
import datetime
from io import StringIO

from django.core.management import call_command
from django.contrib.auth import get_user_model

from celery import shared_task, Task
from celery.utils.log import get_task_logger

from aristotle_mdr.utils.download import get_download_class
from aristole_mdr.models import _concept, RegistrationAuthority

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
    meta.update({"result": run_django_command('update_index', interactive=False)})
    return meta


@shared_task(base=AristotleTask, bind=True, name='long__load_help')
def loadhelp_task(*args, **kwargs):
    meta = {"requester": kwargs['requester'], "start_date": datetime.datetime.now()}
    self.update_state(meta=meta, state="STARTED")
    meta.update({"result": run_django_command('load_aristotle_help')})
    return meta


@shared_task(name='fire_async_signal')
def fire_async_signal(namespace, signal_name, message={}):
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

    raise LookupError('Requested Donwloader class could not be found')


@shared_task(name='send_sandbox_notification_emails')
def send_sandbox_notification_emails(emails_list, user_email, sandbox_access_url):

    from django.core.mail import send_mail

    # Send a separate email to each email address:
    for email in emails_list:
        send_mail(
            'Sandbox Access',
            'Hello there, to access my Sandbox please use the following URL: ' + sandbox_access_url,
            user_email,
            [email]
        )


@shared_task(name='send_notification_email')
def send_notification_email(recipient, message):
    from django.core.mail import send_mail
    from django.conf import settings

    # TODO: CHECK IF THIS SETTING WORKS IN PRODUCTION ENVIRONMENT:

    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        'Notification',
        message,
        from_email,
        [recipient]
    )


@shared_task(name='register_items')
def register_items(ids: List[int], cascade: bool, state: int, ra_id: int,
                   user_id: int, change_details: str, regDate: Tuple[int, int, int]):

    # Get objects from serialized representation
    ra = RegistrationAuthority.objects.get(id=ra_id)
    items = _concept.objects.filter(id__in=ids)
    user = get_user_model().objects.get(id=user_id)
    registration_date = datetime.date(regDate[0], regDate[1], regDate[2])

    # Bulk get subclasses
    items = items.select_subclasses()

    if cascade:
        register_method = ra.cascaded_register
    else:
        register_method = ra.register

    for item in items:
        register_method(
            item,
            state,
            user,
            changeDetails=change_details,
            registrationDate=registration_date
        )
