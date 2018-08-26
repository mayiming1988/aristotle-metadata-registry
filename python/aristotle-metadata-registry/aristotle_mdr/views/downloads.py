from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist

from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_downloaders, downloads as download_utils
from celery.result import AsyncResult as async_result
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

PAGES_PER_RELATED_ITEM = 15


def download(request, download_type, iid):
    """
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

    download_opts = fetch_aristotle_downloaders()
    for kls in download_opts:
        if download_type == kls.download_type:
            try:
                # page size for the pdf
                page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")
                user = getattr(request, 'user', None)
                # properties requested for the file requested
                item_props = {
                    'user': str(user),
                    'view': request.GET.get('view', '').lower(),
                    'page_size': request.GET.get('pagesize', page_size)
                }
                res = kls.download.delay(item_props, iid)
                response = redirect(reverse('aristotle:preparing_download', args=[iid]))
                request.session['download_res_key'] = res.id
                return response
            except TemplateDoesNotExist:
                debug = getattr(settings, 'DEBUG')
                if debug:
                    raise
                # Maybe another downloader can serve this up
                continue

    raise Http404


def bulk_download(request, download_type, items=None):
    """
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
    items=[]

    for iid in request.GET.getlist('items'):
        item = MDR._concept.objects.get_subclass(pk=iid)
        if item.can_view(request.user):
            items.append(item)

    # downloadOpts = fetch_aristotle_settings().get('DOWNLOADERS', [])

    downloadOpts = fetch_aristotle_downloaders()
    for kls in downloadOpts:
        if download_type == kls.download_type:
            try:
                return kls.bulk_download(request, items)
            except TemplateDoesNotExist:
                debug = getattr(settings, 'DEBUG')
                if debug:
                    raise
                # Maybe another downloader can serve this up
                continue

    raise Http404


# Thanks to stackoverflow answer: https://stackoverflow.com/a/23177986
def prepare_async_download(request, identifier):
    res_id = request.session.get('download_res_key', 'no_key')
    if res_id == 'no_key':
        raise Http404
    job = async_result(res_id)
    template = 'aristotle_mdr/downloads/creating_download.html'
    context = {}
    if job.ready():
        return redirect(reverse('aristotle:start_download', args=[identifier]))
    else:
        return render(
            request,
            template,
            context=context
        )

    return HttpResponseBadRequest()


# TODO: need a better redirect architecture, needs refactor.
def get_async_download(request, identifier):
    """
    :param request:
    :param identifier:
    :return:
    """
    res_id = request.session.get('download_res_key', 'no_key')
    if res_id == 'no_key':
        raise Http404
    job = async_result(res_id)
    if not job.successful():
        if job.status == 'PENDING':
            logger.exception('There is no task or you shouldn\'t be on this page yet')
            raise Http404
        else:
            exc = job.get(propagate=False)
            logger.exception('Task {0} raised exception: {1!r}\n{2!r}'.format(
                res_id, exc, job.traceback))
            raise Http404
    job.forget()
    # TODO: Consider moving constant strings in a config or settings file
    doc, mime_type = cache.get(download_utils.get_download_cache_key(identifier, request=request), 'not_cached')
    if doc == 'not_cached':
        # TODO: Need a design to avoid loop and refactor this to redirect to preparing-download
        raise Http404
    return HttpResponse(doc, content_type=mime_type)
