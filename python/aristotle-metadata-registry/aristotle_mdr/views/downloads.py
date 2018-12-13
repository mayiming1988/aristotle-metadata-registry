from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotFound,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.template import TemplateDoesNotExist
from django.views.generic import TemplateView, View, FormView

from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_downloaders, downloads as download_utils
# from aristotle_bg_workers.tasks import download
from aristotle_bg_workers.celery import app
from celery.result import AsyncResult as async_result
from celery import states
from django.core.cache import cache
from django.utils.http import urlencode
from aristotle_mdr import constants as CONSTANTS

import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

PAGES_PER_RELATED_ITEM = 15


class DownloadView(TemplateView):
    """
    Base class inherited by single and bulk download view
    """

    title = 'Auto Generated Content'
    template_name = 'aristotle_mdr/downloads/creating_download.html'
    bulk = False

    def get_item_id_list(self):
        iid = int(self.kwargs['iid'])
        item_ids = [iid]
        return item_ids

    def get(self, request, *args, **kwargs):
        download_type = self.kwargs['download_type']
        item_ids = self.get_item_id_list()

        get_params = request.GET.copy()

        task_args = [download_type, item_ids, request.user.id]
        res = app.send_task(
            'download',
            args=task_args
        )
        # res = download.delay(*task_args)

        downloader_class = None
        dl_classes = fetch_aristotle_downloaders()
        for klass in dl_classes:
            if klass.download_type == download_type:
                downloader_class = klass

        if not downloader_class:
            return HttpResponseNotFound()

        request.session['download_result_id'] = res.id
        # res.forget()
        self.download_type = download_type
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        item_ids = self.get_item_id_list()
        context.update({
            'items': item_ids,
            'file_details': {
                'title': self.request.GET.get('title', self.title),
                'items': 'The item names',
                'format': CONSTANTS.FILE_FORMAT[self.download_type],
                'is_bulk': self.bulk,
                'ttl': int(CONSTANTS.TIME_TO_DOWNLOAD / 60),
                'isReady': False
            }
        })
        return context


class BulkDownloadView(View):
    r"""
    By default, ``aristotle_mdr.views.bulk_download`` is called whenever a URL matches
    the pattern defined in ``aristotle_mdr.urls_aristotle``::

        bulk_download/(?P<download_type>[a-zA-Z0-9\-\.]+)/?

    This is passed into ``bulk_download`` which takes the items GET arguments from the
    request and determines if a user has permission to view the requested items.
    For any items the user can download they are exported in the desired format as
    described in ``aristotle_mdr.views.download``.

    If the requested module is able to be imported, ``downloader.py`` from the given module
    is imported, this file **MUST** have a ``bulk_download`` function defined which returns
    a Django ``HttpResponse`` object of some form.
    """

    def get(request, download_type, items=None):
        items = request.GET.getlist('items')
        download_opts = fetch_aristotle_downloaders()
        get_params = request.GET.copy()
        get_params.setdefault('bulk', True)
        for kls in download_opts:
            if download_type == kls.download_type:
                try:
                    # properties for download template
                    properties = kls.get_bulk_download_config(request, items)
                    if get_params.get('public', False):
                        properties['user'] = False
                    res = kls.bulk_download.delay(properties, items)
                    if not properties.get('title', ''):
                        properties['title'] = 'Auto-generated document'
                    get_params.pop('title')
                    get_params.setdefault('title', properties['title'])
                    response = redirect('{}?{}'.format(
                        reverse('aristotle:preparing_download', args=[download_type]),
                        urlencode(get_params, True)
                    ))
                    download_key = request.session.get(download_utils.get_download_session_key(get_params, download_type))
                    if download_key:
                        async_result(download_key).forget()
                    request.session[download_utils.get_download_session_key(get_params, download_type)] = res.id
                    return response
                except TemplateDoesNotExist:
                    # Maybe another downloader can serve this up
                    continue

        raise Http404


class DownloadStatusView(View):
    """
    This view lets user know that the download is being prepared.
    Checks:
    1. check if there is a celery task id present in the session.
    2. check if the celery task id expired/already downloaded.
    3. check if the job is ready.
    :param request: request object from the API call.
    :param download_type: type of download
    :return: appropriate HTTP response object
    """

    template_name = 'aristotle_mdr/downloads/creating_download.html'

    def get(self, request, *args, **kwargs):
        download_key = 'download_result_id'

        # Check if the job exists
        res_id = request.session[download_key]
        job = async_result(res_id)

        context = {
            'is_ready': False,
            'is_expired': False,
            'state': job.state,
            'file_details': {}
        }

        if job.ready():
            if type(job.result) == bool:
                context['file_details']['result'] = job.result
            context['is_ready'] = True
            context['is_expired'] = False

        # job.forget()
        return JsonResponse(context)


class GetDownloadFileView(View):
    """
    This will return the download if the download is cached in redis.
    Checks:
    1. check if the download has expired
    2. check if there is no key to download. If there is not
    :param request:
    :param download_type: type of download
    :return:
    """

    def get(self, request, *args, **kwargs):
        items = request.GET.getlist('items', None)
        download_key = 'download_result_id'

        try:
            res_id = request.session[download_key]
        except KeyError:
            logger.exception('There is no key for request')
            raise Http404

        job = async_result(res_id)

        if not job.successful():
            if job.status == 'PENDING':
                logger.exception('There is no task or you shouldn\'t be on this page yet')
                raise Http404
            else:
                exc = job.get(propagate=False)
                logger.exception('Task {0} raised exception: {1!r}\n{2!r}'.format(res_id, exc, job.traceback))
                return HttpResponseServerError('cant produce document, Try again')

        # job.forget()
        try:
            doc, mime_type, properties = cache.get(
                download_utils.get_download_cache_key(items, request=request, download_type=download_type),
                (None, '', '')
            )
        except ValueError:
            logger.exception('Should unpack 3 values from the cache', ValueError)
            return HttpResponseServerError('Cant unpack values')
        if not doc:
            # TODO: Need a design to avoid loop and refactor this to redirect to preparing-download
            return HttpResponseServerError('No document in cache')
        response = HttpResponse(doc, content_type=mime_type)
        response['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(request.GET.get('title'), download_type)
        for key, val in properties.items():
                response[key] = val
        del request.session[download_key]
        return response


class DownloadOptionsView(FormView):
    """
    Form with options before the download
    """
    pass
