from typing import List, Dict, Any, Iterable
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
from aristotle_bg_workers.tasks import download
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


class BaseDownloadView(TemplateView):
    """
    Base class inherited by single and bulk download views below
    """

    title = 'Auto Generated Content'
    template_name = 'aristotle_mdr/downloads/creating_download.html'
    bulk = False

    def get_item_id_list(self) -> List[int]:
        """Returns a list of item ids"""
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        download_type = self.kwargs['download_type']
        self.item_ids = self.get_item_id_list()

        get_params = request.GET.copy()

        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            user_id = None

        task_args = [download_type, item_ids, user_id]
        res = download.delay(*task_args)

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

    def get_item_names(self) -> Iterable[str]:
        name_list = MDR._concept.objects.filter(id__in=self.item_ids).values_list('name', flat=True)
        return name_list

    def get_file_title(self, item_names: Iterable[str]) -> str:
        """Should be overwritten"""
        return 'Item Download'

    def get_file_details(self) -> Dict[str, Any]:
        item_names = self.get_item_names()
        return {
            'title': self.get_file_title(),
            'items': ', '.join(item_names),
            'format': CONSTANTS.FILE_FORMAT[self.download_type],
            'is_bulk': len(self.item_ids) > 1,
            'isReady': False
        }

    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)

        context.update({
            'items': self.item_ids,
            'file_details': self.get_file_details()
        })
        return context


class DownloadView(BaseDownloadView):

    def get_item_id_list(self):
        iid = int(self.kwargs['iid'])
        item_ids = [iid]
        return item_ids

    def get_file_title(self, item_names):
        return item_names[0] + ' Download'


class BulkDownloadView(BaseDownloadView):

    def get_item_id_list(self):
        return request.GET.getlist('items')

    def get_file_title(self, item_names):
        return 'Bulk Download'


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

    def get(self, request, *args, **kwargs):
        download_key = 'download_result_id'

        # Check if the job exists
        try:
            res_id = request.session[download_key]
        except KeyError:
            return HttpResponseNotFound()

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
