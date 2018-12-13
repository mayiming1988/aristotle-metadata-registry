from typing import Any, List
from aristotle_mdr.utils import get_download_template_path_for_item

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.core.cache import cache

import io
import csv
from aristotle_mdr.contrib.help.models import ConceptHelp
from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import downloads as download_utils
from celery import shared_task
from aristotle_mdr import constants as CONSTANTS


class DownloaderBase:
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
    icon_class: str = ""
    description: str = ""
    # A unique identifier for the downloader (used in url and passed to task)
    download_type: str

    default_options = {
        'include_supporting': False,
        'subclasses': [],
        'front_page': None,
        'back_page': None,
        'email_to_user': False
    }

    def __init__(self, item_ids: List[int], user_id: int, options: Dict[str, Any]={}):
        self.item_ids = item_ids
        self.error = False

        self.items = MDR._concept.objects.filter(id__in=item_ids).select_subclasses()
        self.user = get_user_model().filter(id=user_id)

        self.options = self.default_options.copy()
        self.options.update(options)

    @property
    def bulk(self):
        return len(self.item_ids) > 1

    def download(self):
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

    def get_cache_key(self):
        return download_utils.get_download_cache_key(
            self.item_ids,
            self.user,
            download_type=self.download_type
        )

    def store_file(self, value, ttl=CONSTANTS.TIME_TO_DOWNLOAD):
        """
        This is the cache interface for all the download types.
        :param key: Key is the combination of iid(s)
        :param value: value is the value to be stored in the cache
        :param ttl: It's the time to live for the cache storage
        :return: returns None.
        """
        key = self.get_cache_key()
        cache.set(key, value, ttl)


# Deprecated
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
