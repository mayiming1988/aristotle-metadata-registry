from typing import Any


import io
import csv
from aristotle_mdr.contrib.help.models import ConceptHelp
from aristotle_mdr import models as MDR
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import downloads as download_utils
from celery import shared_task
from django.core.cache import cache
from aristotle_mdr import constants as CONSTANTS


class DownloaderBase(object):
    """
    Required class properties:

    * description: a description of the downloader type
    * download_type: the extension or name of the download to support
    * icon_class: the font-awesome class
    * metadata_register: can be one of:

      * a dictionary with keys corresponding to django app labels and values as lists of models within that app the downloader supports
      * the string "__all__" indicating the downloader supports all metadata types
      * the string "__template__" indicating the downloader supports any metadata type with a matching download template
    """
    metadata_register: Any = {}
    icon_class = ""
    description = ""

    @classmethod
    def get_download_config(cls, request, iid):
        """
        This method must be overriden. This method takes in a request object and item and
        creates a download config for the download method.
        This returns config created and item/iid
        """
        raise NotImplementedError

    @classmethod
    def get_bulk_download_config(cls, request, items):
        r"""
        This method must be overriden. This takes request object and returns a computed set of download config
        creates a dict of properties required to generate bulk_downloads
        -> properties must contain url_id to identify an unique download url of the format ([\w\-\. ]+)/?$
        :param request: request object from the client
        :param items: items to download
        :return: The set of properties required by bulk_download method
        """
        raise NotImplementedError

    @staticmethod
    def download(properties, iid):
        """
        This method must be overriden and return the downloadable object of appropriate type
        and mime type for the object
        This is a static method because it is a celery task
        This method should return 2 objects and an optional third
        first object is item
        second item is the mime type
        third object a list of tuple(key, value) which specifies the response object properties
        Example implementation is in CSVDownloader.download method

        User this in a celery task to get the item from iid
        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)
        """
        raise NotImplementedError

    @staticmethod
    def bulk_download(properties, item):
        """
        This method must be overriden and
        return a bulk downloaded set of items in an appropriate file format and
        mime type for the object
        This is a static method because it is a celery task
        """
        raise NotImplementedError

    @classmethod
    def get_cache_key(cls, user, iids=[]):
        return download_utils.get_download_cache_key(iids, user, download_type=cls.download_type)

    @staticmethod
    def cache_file(key, value, ttl=CONSTANTS.TIME_TO_DOWNLOAD):
        """
        This is the cache interface for all the download types.
        :param key: Key is the combination of iid(s)
        :param value: value is the value to be stored in the cache
        :param ttl: It's the time to live for the cache storage
        :return: returns None.
        """
        cache.set(key, value, ttl)


class CSVDownloader(DownloaderBase):
    download_type = "csv-vd"
    metadata_register = {'aristotle_mdr': ['valuedomain']}
    label = "CSV list of values"
    icon_class = "fa-file-excel-o"
    description = "CSV downloads for value domain codelists"

    @classmethod
    def get_download_config(cls, request, iid):
        user = getattr(request, 'user', None)
        properties = {
            'user': None,
            'title': cls.item.name
        }
        if user:
            properties['user'] = str(user)
        return properties

    @classmethod
    def bulk_download(cls, request, item):
        raise NotImplementedError

    @staticmethod
    @shared_task(name='aristotle_mdr.downloader.CSVDownloader.download')
    def download(properties, iid):
        """Built in download method"""
        User = get_user_model()
        user = properties.get('user')
        if user and user != str(AnonymousUser()):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()

        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)

        mem_file = io.StringIO()
        writer = csv.writer(mem_file)
        writer.writerow(['value', 'meaning', 'start date', 'end date', 'role'])
        for v in item.permissibleValues.all():
            writer.writerow(
                [v.value, v.meaning, v.start_date, v.end_date, "permissible"]
            )
        for v in item.supplementaryValues.all():
            writer.writerow(
                [v.value, v.meaning, v.start_date, v.end_date, "supplementary"]
            )
        CSVDownloader.cache_file(CSVDownloader.get_cache_key(user, iid),
                                 (mem_file.getvalue(),
                                  'txt/csv',
                                  {'Content-Disposition': 'attachment; filename="{}.csv"'.format(item.name)}
                                  )
                                 )
        return iid


def items_for_bulk_download(items, user):
    iids = {}
    item_querysets = {}  # {PythonClass:{help:ConceptHelp,qs:Queryset}}

    for item in items:
        if item and item.can_view(user):
            if item.__class__ not in iids.keys():
                iids[item.__class__] = []
            iids[item.__class__].append(item.pk)

            for metadata_type, qs in item.get_download_items():
                if metadata_type not in item_querysets.keys():
                    item_querysets[metadata_type] = {'help': None, 'qs': qs}
                else:
                    item_querysets[metadata_type]['qs'] |= qs

    for metadata_type, ids_set in iids.items():
        query = metadata_type.objects.filter(pk__in=ids_set)
        if metadata_type not in item_querysets.keys():
            item_querysets[metadata_type] = {'help': None, 'qs': query}
        else:
            item_querysets[metadata_type]['qs'] |= query

    for metadata_type in item_querysets.keys():
        item_querysets[metadata_type]['qs'] = item_querysets[metadata_type]['qs'].distinct().visible(user)
        item_querysets[metadata_type]['help'] = ConceptHelp.objects.filter(
            app_label=metadata_type._meta.app_label,
            concept_type=metadata_type._meta.model_name
        ).first()

    return item_querysets
