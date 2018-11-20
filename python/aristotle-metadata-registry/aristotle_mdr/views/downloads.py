from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist

from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_downloaders, downloads as download_utils
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


def download(request, download_type, iid=None):
    r"""
    By default, ``aristotle_mdr.views.download`` is called whenever a URL matches
    the pattern defined in ``aristotle_mdr.urls_aristotle``::

        download/(?P<download_type>[a-zA-Z0-9\-\.]+)/(?P<iid>\d+)/?

    This is passed into ``download`` which resolves the item id (``iid``), and
    determines if a user has permission to view the requested item with that id. If
    a user is allowed to download this file, ``download`` iterates through each
    download type defined in ``ARISTOTLE_SETTINGS.DOWNLOADERS``.

    A download option tuple takes the following form form::

        ('file_type','display_name','font_awesome_icon_name','module_name'),

    With ``file_type`` allowing only ASCII alphanumeric and underscores,
    ``display_name`` can be any valid python string,
    ``font_awesome_icon_name`` can be any Font Awesome icon and
    ``module_name`` is the name of the python module that provides a downloader
    for this file type.

    For example, the Aristotle-PDF with Aristotle-MDR is a PDF downloader which has the
    download definition tuple::

            ('pdf','PDF','fa-file-pdf-o','aristotle_pdr'),

    Where a ``file_type`` multiple is defined multiple times, **the last matching
    instance in the tuple is used**.

    Next, the module that is defined for a ``file_type`` is dynamically imported using
    ``exec``, and is wrapped in a ``try: except`` block to catch any exceptions. If
    the ``module_name`` does not match the regex ``^[a-zA-Z0-9\_]+$`` ``download``
    raises an exception.

    If the module is able to be imported, ``downloader.py`` from the given module
    is imported, this file **MUST** have a ``download`` function defined which returns
    a Django ``HttpResponse`` object of some form.
    """
    item = MDR._concept.objects.get_subclass(pk=iid)
    item = get_if_user_can_view(item.__class__, request.user, iid)
    if not item:
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied
    get_params = request.GET.copy()
    get_params.setdefault('items', iid)
    download_opts = fetch_aristotle_downloaders()
    for kls in download_opts:
        if download_type == kls.download_type:
            try:
                # properties requested for the file requested
                kls.item = item
                properties = kls.get_download_config(request, iid)
                if get_params.get('public', False):
                    properties['user'] = False
                res = kls.download.delay(properties, iid)
                get_params.setdefault('title', properties.get('title', 'Auto-Generated Document'))
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
                debug = getattr(settings, 'DEBUG')
                if debug:
                    raise
                # Maybe another downloader can serve this up
                continue

    raise Http404


def bulk_download(request, download_type, items=None):
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

    # downloadOpts = fetch_aristotle_settings().get('DOWNLOADERS', [])
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
                debug = getattr(settings, 'DEBUG')
                if debug:
                    raise
                # Maybe another downloader can serve this up
                continue

    raise Http404


# Thanks to stackoverflow answer: https://stackoverflow.com/a/23177986
def prepare_async_download(request, download_type):
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
    try:
        get_params = request.GET.copy()
        items = get_params.getlist('items')
    except KeyError:
        return HttpResponseBadRequest()

    download_key = download_utils.get_download_session_key(get_params, download_type)

    if get_params.get('format', False):
        get_params.pop('format')
    start_new_download = False
    try:
        # Check if the job exists
        res_id = request.session[download_key]
        job = async_result(res_id)
        if job.status == states.PENDING:
            # make sure you don't call a forget in the rest of the function or else it will go into infinite loop
            del request.session[download_key]
            job.forget()
            # Raising key error because key is invalid
            raise KeyError
    except KeyError:
        start_new_download = True

    if start_new_download:
        if get_params.get('bulk'):
            redirect_url = reverse('aristotle:bulk_download', args=[download_type])
        else:
            redirect_url = reverse('aristotle:download', args=[download_type, items[0]])

        return redirect('{}?{}'.format(
            redirect_url,
            urlencode(get_params, True)
        ))

    template = 'aristotle_mdr/downloads/creating_download.html'
    context = {}
    download_url = '{}?{}'.format(
        reverse('aristotle:start_download', args=[download_type]),
        urlencode(get_params, True)
    )
    context['items'] = items
    context['file_details'] = {
        'title': request.GET.get('title', 'Auto Generated Document'),
        'items': ', '.join([MDR._concept.objects.get_subclass(pk=int(iid)).name for iid in items]),
        'format': CONSTANTS.FILE_FORMAT[download_type],
        'is_bulk': request.GET.get('bulk', False),
        'ttl': int(CONSTANTS.TIME_TO_DOWNLOAD / 60),
        'isReady': False
    }

    if job.ready():
        context['file_details']['download_url'] = download_url
        context['is_ready'] = True
        context['is_expired'] = False
        if not cache.get(download_utils.get_download_cache_key(items, request=request, download_type=download_type)):
            context['is_expired'] = True
            del request.session[download_key]
            job.forget()

    if request.GET.get('format') == 'json':
        return JsonResponse(context)

    return render(request, template, context=context)


# TODO: need a better redirect architecture, needs refactor.
def get_async_download(request, download_type):
    """
    This will return the download if the download is cached in redis.
    Checks:
    1. check if the download has expired
    2. check if there is no key to download. If there is not
    :param request:
    :param download_type: type of download
    :return:
    """
    items = request.GET.getlist('items', None)
    debug = getattr(settings, 'DEBUG')
    download_key = download_utils.get_download_session_key(request.GET, download_type)
    try:
        res_id = request.session[download_key]
    except KeyError:
        logger.exception('There is no key for request')
        if debug:
            raise
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

    job.forget()
    try:
        doc, mime_type, properties = cache.get(
            download_utils.get_download_cache_key(items, request=request, download_type=download_type),
            (None, '', '')
        )
    except ValueError:
        if debug:
            raise
        logger.exception('Should unpack 3 values from the cache', ValueError)
        return HttpResponseServerError('Cant unpack values')
    if not doc:
        if debug:
            raise ValueError('No document in the cache')
        # TODO: Need a design to avoid loop and refactor this to redirect to preparing-download
        return HttpResponseServerError('No document in cache')
    response = HttpResponse(doc, content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(request.GET.get('title'), download_type)
    for key, val in properties.items():
            response[key] = val
    del request.session[download_key]
    return response
