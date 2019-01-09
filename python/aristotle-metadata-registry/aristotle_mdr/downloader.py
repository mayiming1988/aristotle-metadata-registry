from typing import Any, List, Dict, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import get_storage_class
from django.core.files import File
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

import io
import csv
from hashlib import sha256
import pickle

from aristotle_mdr.contrib.help.models import ConceptHelp
from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_settings
from aristotle_mdr.utils.utils import get_download_template_path_for_item
from celery import shared_task


class Downloader:
    """
    Base class used by all downloaders
    Subclasses must override the create_file method

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
    icon_class: str = 'fa-file-text-o'
    description: str = ""
    filename: str = 'download'
    allow_wrapper_pages: bool = False  # Whether to allow a front and back page
    # A unique identifier for the downloader (used in url and passed to task)
    download_type: str = ''
    file_extension: str = ''

    default_options = {
        'include_supporting': False,
        'subclasses': None,
        'front_page': None,
        'back_page': None,
        'email_to_user': False
    }

    def __init__(self, item_ids: List[int], user_id: Optional[int], options: Dict[str, Any]={}):
        self.item_ids = item_ids
        self.error = False

        if user_id is not None:
            self.user = get_user_model().objects.get(id=user_id)
        else:
            self.user = AnonymousUser()

        self.items = MDR._concept.objects.filter(id__in=item_ids).visible(self.user).select_subclasses()

        # Shallow copy of options
        self.options = self.default_options.copy()
        self.options.update(options)

    def create_file(self) -> File:
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

    @property
    def bulk(self):
        return len(self.item_ids) > 1

    def get_filepath(self):
        if self.user.is_authenticated:
            userpart = str(self.user.id)
        else:
            userpart = 'anon'

        arghash = sha256()
        arghash.update(pickle.dumps(self.item_ids))
        arghash.update(pickle.dumps(self.options))

        fname = '/'.join([userpart, arghash.hexdigest(), self.filename])
        if self.file_extension:
            return '.'.join([fname, self.file_extension])

        return fname

    def retrieve_file(self, filename: str) -> Optional[str]:
        """Use defualt storage class to retrieve file if it exists"""
        storage_class = get_storage_class()
        storage = storage_class()
        if storage.exists(filename):
            return storage.url(filename)

    def store_file(self, filename: str, content: File) -> str:
        """Use default storage class to store file"""
        storage_class = get_storage_class()
        storage = storage_class()
        storage.save(filename, content)
        return storage.url(filename)

    def download(self) -> str:
        """Get the url for this downloads file, creating it if neccesary"""
        filepath = self.get_filepath()

        url = self.retrieve_file(filepath)
        if url is not None:
            return url

        fileobj = self.create_file()
        return self.store_file(filepath, fileobj)

    @classmethod
    def get_class_info(cls) -> Dict[str, Any]:
        return {
            'icon_class': cls.icon_class
        }


class HTMLDownloader(Downloader):
    """
    Generates a html download
    This is subclassed for other formats that are generated from html
    such as the pdf downloader
    """

    download_type = 'html'
    file_extension = 'html'
    label = 'HTML'
    metadata_register = '__all__'
    description = 'Download as html (used for debugging)'

    bulk_download_template = 'aristotle_mdr/downloads/pdf/bulk_download.html'

    def get_base_download_context(self) -> Dict[str, Any]:
        # page size for the pdf
        aristotle_settings = fetch_aristotle_settings()
        page_size = aristotle_settings.get('PDF_PAGE_SIZE', 'A4')

        context = {
            'user': self.user,
            'page_size': page_size,
        }

        if self.options['include_supporting']:
            context['view'] = 'technical'
        else:
            context['view'] = 'simple'

        return context

    def get_download_context(self) -> Dict[str, Any]:
        """
        Create configuration for pdf download method
        :param request: request object
        :param iid: id of the item requested
        :return: properties for item, id of the item
        """
        context = self.get_base_download_context()

        item = self.items[0]
        sub_items = [
            (obj_type, qs.visible(self.user).order_by('name').distinct())
            for obj_type, qs in item.get_download_items()
        ]

        context.update({
            'title': item.name,
            'item': item,
            'subitems': sub_items,
            'tableOfContents': len(sub_items) > 0,
        })

        return context

    def get_bulk_download_context(self) -> Dict[str, Any]:
        """
        generate properties for pdf document
        :param request: API request object
        :param items: items to download
        :return: properties computed, items
        """
        context = self.get_base_download_context()

        _list = "<li>" + "</li><li>".join([item.name for item in self.items if item]) + "</li>"
        subtitle = mark_safe("Generated from the following metadata items:<ul>%s<ul>" % _list)

        item_querysets = items_for_bulk_download(self.items, self.user)

        context.update({
            'title': 'Auto-generated document',
            'subtitle': subtitle,
            'items': self.items,
            'included_items': sorted(
                [(k, v) for k, v in item_querysets.items()],
                key=lambda k_v: k_v[0]._meta.model_name
            ),
        })
        return context

    def get_context(self) -> Dict[str, Any]:
        """
        Gets the template context
        Can be used by subclasses
        """
        if self.bulk:
            return self.get_bulk_context()
        else:
            return self.get_download_context()

    def get_template(self) -> str:
        """
        Gets the template context
        Can be used by subclasses
        """
        if self.bulk:
            return self.bulk_download_template
        else:
            item = self.items[0]
            # Template folder should be renamed to html
            return get_download_template_path_for_item(item, 'pdf')

    def get_html(self) -> bytes:
        """
        Gets the rendered html string
        Can be used by subclasses
        """
        template = self.get_template()
        context = self.get_context()
        safestring = render_to_string(template, context=context)
        return str(safestring).encode()

    def create_file(self):
        html = self.get_html()
        return ContentFile(html)


# Deprecated
class CSVDownloader(Downloader):
    download_type = "csv-vd"
    file_extension = 'csv'
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
