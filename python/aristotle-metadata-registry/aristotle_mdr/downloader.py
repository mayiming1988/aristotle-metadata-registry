from typing import Any, List, Dict, Optional, Union, Tuple, AnyStr, Iterable

from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.storage import get_storage_class
from django.core.files import File
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.module_loading import import_string

import io
import csv
from hashlib import sha256
import pickle
import pypandoc

from aristotle_mdr.contrib.help.models import ConceptHelp
from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_settings, get_model_label
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
    metadata_register: Union[Dict[str, List], str] = '__all__'
    icon_class: str = 'fa-file-text-o'
    description: str = ''
    filename: str = 'download'
    allow_wrapper_pages: bool = False  # Whether to allow a front and back page
    # A unique identifier for the downloader (used in url and passed to task)
    download_type: str = ''
    file_extension: str = ''
    requires_pandoc: bool = False

    default_options = {
        'include_supporting': False,
        'include_related': False,
        'subclasses': None,
        'front_page': None,
        'back_page': None,
        'email_to_user': False
    }

    def __init__(self, item_ids: List[int], user_id: Optional[int], options: Dict[str, Any]={}):
        self.item_ids = item_ids
        self.error = False

        if user_id is not None:
            self.user = get_user_model().objects.prefetch_related('profile').get(id=user_id)
        else:
            self.user = AnonymousUser()

        self.items = MDR._concept.objects.filter(id__in=item_ids).visible(self.user).select_subclasses()

        # Do len here since we are going to evaluate it later anyways
        self.numitems = len(self.items)
        self.bulk = (self.numitems > 1)

        if self.numitems == 0:
            raise PermissionDenied('User does not have permission to view any items')

        # Shallow copy of options
        self.options = self.default_options.copy()
        self.options.update(options)

    def create_file(self) -> File:
        """
        This method must be overriden and return the downloadable object of appropriate type and mime type for the object This is a static method because it is a celery task This method should return 2 objects and an optional third first object is item second item is the mime type third object a list of tuple(key, value) which specifies the response object properties Example implementation is in CSVDownloader.download method
        User this in a celery task to get the item from iid
        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)
        """
        raise NotImplementedError

    def get_storage(self):
        if settings.DOWNLOADS_STORAGE is not None:
            storage_class = import_string(settings.DOWNLOADS_STORAGE)
        else:
            storage_class = get_storage_class()
        return storage_class()

    @property
    def has_wrap_pages(self):
        return (self.options['front_page'] is not None or self.options['back_page'] is not None)

    def get_wrap_pages(self) -> List:
        if not self.allow_wrapper_pages:
            return [None, None]

        storage = self.get_storage()
        pages = []
        for page_name in ['front_page', 'back_page']:
            page_path = self.options[page_name]
            if page_path is not None:
                with storage.open(page_path) as page_file:
                    pages.append(page_file.read())
            else:
                pages.append(None)

        return pages

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
        """Use default storage class to retrieve file if it exists"""
        storage = self.get_storage()
        if storage.exists(filename):
            file_modified = storage.get_modified_time(filename)
            for item in self.items:
                # If one of the items has been modified after the file
                if item.modified > file_modified:
                    storage.delete(filename)
                    return None
            # If the file was modified after the items
            return storage.url(filename)
        return None

    def store_file(self, filename: str, content: File) -> str:
        """Use default storage class to store file"""
        storage = self.get_storage()
        # Filename can change if a file already exists
        # (wont happen unless caching is off)
        final_fname = storage.save(filename, content)
        return storage.url(final_fname)

    def download(self) -> str:
        """Get the url for this downloads file, creating it if neccesary"""
        filepath = self.get_filepath()

        if settings.DOWNLOAD_CACHING:
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
    such as the pdf downloader. But can be enabled for testing purposes
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
            'options': self.options
        }
        return context

    def get_download_context(self) -> Dict[str, Any]:
        """
        Return context for single item download
        """
        context = self.get_base_download_context()

        # This will raise an exception if the list is empty, but thats ok
        item = self.items[0]
        sub_items = self.get_sub_items_dict()

        context.update({
            'title': item.name,
            'item': item,
            'subitems': sub_items,
            'tableOfContents': len(sub_items) > 0,
        })

        return context

    def _add_to_sub_items(self, items_dict, item):
        item_class = type(item)
        label = get_model_label(item_class)
        if label not in items_dict:
            model_help = ConceptHelp.objects.filter(
                app_label=item_class._meta.app_label,
                concept_type=item_class._meta.model_name
            ).first()
            items_dict[label] = {
                'items': [],
                'verbose_name': item_class.get_verbose_name(),
                'verbose_name_plural': item_class.get_verbose_name_plural(),
                'help': model_help
            }
        items_dict[label]['items'].append(item)

    def get_sub_items_dict(self, include_root=False) -> Dict[str, Dict[str, Any]]:
        items = {}

        # Get all items using above method to create dict
        for item in self.items:
            # include_root includes the selected items in the dict
            if include_root:
                self._add_to_sub_items(items, item)

            for dl_item in item.get_download_items():
                if isinstance(dl_item, QuerySet):
                    sub_list = list(dl_item.visible(self.user))
                else:
                    sub_list = [dl_item]

                for sub_item in sub_list:
                    self._add_to_sub_items(items, sub_item)

        # Sort the items lists by name
        for label, data in items.items():
            data['items'].sort(key=lambda item: item.name)

        return items

    def get_bulk_download_context(self) -> Dict[str, Any]:
        """
        Return context for bulk download
        """
        context = self.get_base_download_context()

        _list = "<li>" + "</li><li>".join([item.name for item in self.items if item]) + "</li>"
        subtitle = mark_safe("Generated from the following metadata items:<ul>%s<ul>" % _list)

        sub_items = self.get_sub_items_dict()

        context.update({
            'subtitle': subtitle,
            'items': self.items,
            'included_items': sub_items
        })
        return context

    def get_context(self) -> Dict[str, Any]:
        """
        Gets the template context
        Can be used by subclasses
        """
        if self.bulk:
            return self.get_bulk_download_context()
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
            # This will raise an exception if the list is empty, but thats ok
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


class PandocDownloader(HTMLDownloader):
    """
    Used as base class for downloader converting html to other
    formats via pandoc. Does not work as a downloader itself
    """

    requires_pandoc = True

    def convert_html(self, html) -> AnyStr:
        raise NotImplementedError

    def create_file(self):
        html = self.get_html()
        string = self.convert_html(html)
        return ContentFile(string)


class DocxDownloader(PandocDownloader):

    download_type = 'docx'
    file_extension = 'docx'
    label = 'Word'
    metadata_register = '__all__'
    icon_class = 'fa-file-word-o'
    description = 'Download as word document'

    def convert_html(self, html):
        return pypandoc.convert_text(html, 'docx', format='html', return_bytes=True)


class ODTDownloader(PandocDownloader):

    download_type = 'odt'
    file_extension = 'odt'
    label = 'ODT'
    metadata_register = '__all__'
    icon_class = 'fa-file-word-o'
    description = 'Download as odt document'

    def convert_html(self, html):
        return pypandoc.convert_text(html, 'odt', format='html', return_bytes=True)


class MarkdownDownloader(PandocDownloader):

    download_type = 'md'
    file_extension = 'md'
    label = 'Markdown'
    metadata_register = '__all__'
    description = 'Download as markdown'

    def convert_html(self, html):
        return pypandoc.convert_text(html, 'md', format='html')
