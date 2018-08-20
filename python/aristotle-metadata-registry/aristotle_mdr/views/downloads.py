from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist

from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_downloaders
from celery.result import AsyncResult as async_result
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

PAGES_PER_RELATED_ITEM = 15


def download(request, download_type, iid=None):
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

    downloadOpts = fetch_aristotle_downloaders()
    for kls in downloadOpts:
        if download_type == kls.download_type:
            try:
                # page size for the pdf
                page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")
                user = getattr(request, 'user', None)
                # properties requested for the file requested
                # TODO: Consider using a dict to explain a user like user: {email: email@id.com}
                item_props = {
                    'user': None if not user.is_authenticated else user.email,
                    'view': request.GET.get('view', '').lower(),
                    'page_size': request.GET.get('pagesize', page_size)
                }

                # Calling async if present else fallback on sync method
                if 'async_download' in dir(kls):
                    res = kls.async_download.delay(item_props, iid)
                    response = redirect(reverse('aristotle:preparing_download', args=[iid]))
                    response.set_cookie('download_res_key', res.id)
                    return response
                else:
                    return kls.download(request, iid)
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


def get_download_cache_key(identifier, user_pk=None, request=None):
    """
    Returns a unique to cache key using a specified key(user_pk) or from a request.
    Can send user's unique key, a request or id
    The preference is given in order `id:user_pk` | `id:request.user.email` | `id`
    :param identifier: identifier for the job
    :param user_pk: user's unique id such as email or database id
    :param request: session request
    :return: string with a unique id
    """
    if user_pk:
        return '{}:{}'.format(identifier, user_pk)
    elif request:
        user = request.user
        unique_key = str(user)
        return '{}:{}'.format(identifier, unique_key)
    else:
        return '{}'.format(identifier)


# Thanks to stackoverflow answer: https://stackoverflow.com/a/23177986
def prepare_async_download(request, identifier):
    res_id = request.COOKIES.get('download_res_key')
    job = async_result(res_id)
    template = 'aristotle_mdr/downloads/creating_download.html'
    context = {}
    logger.info(job.ready())
    if job.ready():
        try:
            return redirect(reverse('aristotle:start_download', args=[identifier]))
        except Exception as exception:
            if getattr(settings, 'DEBUG'):
                logger.error('could not get the '.format(exception))
                raise
            pass
    else:
        return render(
            request,
            template,
            context=context
        )

    return HttpResponseBadRequest()

def get_async_download(request, identifier):
    res_id = request.COOKIES.get('download_res_key')
    job = async_result(res_id)
    logger.info(job.successful())
    if not job.successful():
        exc = job.get(propagate=False)
        logger.exception('Task {0} raised exception: {1!r}\n{2!r}'.format(
          res_id, exc, job.traceback))
        return HttpResponseBadRequest()
    res = job.get()
    return HttpResponse(cache.get(identifier), content_type='application/pdf')

