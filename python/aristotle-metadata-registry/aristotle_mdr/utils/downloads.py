from importlib import import_module

from django.conf import settings

from aristotle_mdr import exceptions as registry_exceptions


def get_download_module(module_name):
    import re
    if not re.search(r'^[a-zA-Z0-9\_\.]+$', module_name):  # pragma: no cover
        # bad module_name
        raise registry_exceptions.BadDownloadModuleName("Download name isn't a valid Python module name.")
        return import_module("%s.downloader" % module_name)


def get_download_cache_key(identifier=[], user_pk=None, request=None, download_type='txt', delimiter=':'):
    """
    Returns a unique to cache key using a specified key(user_pk) or from a request.
    Can send user's unique key, a request or id
    The preference is given in order `id:user_pk` | `id:request.user.email` | `id`
    :param identifier: identifier for the job
    :param user_pk: user's unique id such as email or database id
    :param request: session request
    :return: string with a unique id
    """
    # Serializing identifier List
    if type(identifier) == list:
        identifier.sort()
        identifier = '-'.join(identifier)

    d = delimiter
    if user_pk:
        key = '{}{}{}{}{}'.format(download_type, d, identifier, d, user_pk)
    elif request:
        user = getattr(request, 'user', None)
        unique_key = str(user)
        key = '{}{}{}{}{}'.format(download_type, d, identifier, d, unique_key)
    else:
        key = '{}{}{}'.format(download_type, d, identifier)

    return key
