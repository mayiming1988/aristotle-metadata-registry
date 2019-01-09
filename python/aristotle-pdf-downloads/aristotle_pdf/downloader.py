from aristotle_mdr.utils import get_download_template_path_for_item
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr import models as MDR

import os

from django.conf import settings
from django.template.loader import select_template, get_template
from django.template import Context
from django.utils.safestring import mark_safe
from celery import shared_task

from aristotle_mdr.contrib.help.models import ConceptHelp

from aristotle_mdr.downloader import DownloaderBase

import logging
import weasyprint

item_register = {
    'pdf': '__template__'
}

PDF_STATIC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pdf_static')

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class PDFDownloader(DownloaderBase):
    download_type = "pdf"
    metadata_register = '__template__'
    label = "PDF"
    icon_class = "fa-file-pdf-o"
    description = "Downloads for various content types in the PDF format"

    @classmethod
    def get_download_config(cls, request, iid):
        """
        Create configuration for pdf download method
        :param request: request object
        :param iid: id of the item requested
        :return: properties for item, id of the item
        """
        # page size for the pdf
        page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")
        user = getattr(request, 'user', None)

        item_props = {
            'user': None,
            'view': request.GET.get('view', '').lower(),
            'page_size': request.GET.get('pagesize', page_size),
            'title': cls.item.name
        }

        if user:
            item_props['user'] = str(user)
        return item_props

    @staticmethod
    @shared_task(name='aristotle_pdf_downloads.downloader.download')
    def download(properties, iid):
        """Built in download method
        create pdf_context and return the results to celery backend.
        :param properties: properties of the pdf template to be generated
        :param iid: id of the item
        :return: return the iid of the task
        """
        User = get_user_model()
        user = properties['user']
        if user and user != str(AnonymousUser()):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()
        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)
        template = get_download_template_path_for_item(item, PDFDownloader.download_type)

        sub_items = [
            (obj_type, qs.visible(user).order_by('name').distinct())
            for obj_type, qs in item.get_download_items()
        ]

        PDFDownloader.cache_file(PDFDownloader.get_cache_key(user, iid), (render_to_pdf(template, {
            'title': properties['title'],
            'item': item,
            'subitems': sub_items,
            'tableOfContents': len(sub_items) > 0,
            'view': properties['view'].lower(),
            'pagesize': properties['page_size'],
        }), 'application/pdf', {}))

        return iid

    @classmethod
    def get_bulk_download_config(cls, request, items):
        """
        generate properties for pdf document
        :param request: API request object
        :param items: items to download
        :return: properties computed, items
        """
        user = getattr(request, 'user', None)

        properties = {
            'user': None,
            'title': request.GET.get('title', '').strip() or 'Auto-generated document',
            'subtitle': request.GET.get('subtitle', None),
            'debug_as_html': request.GET.get('html', False),
            'page_size': request.GET.get('pagesize', None),
            # TODO: will fail for parallel download for a single user
            # if this document is title is not specified for more than one documents. Use items instead
            'url_id': request.GET.get('title', None) or 'Auto-generated document',
        }
        if user:
            properties['user'] = str(user)
        return properties

    @staticmethod
    @shared_task(name='aristotle_pdf_downloads.downloader.bulk_download')
    def bulk_download(properties, iids=[], title=None, subtitle=None):
        """Built in download method"""
        items = []
        User = get_user_model()
        template = 'aristotle_mdr/downloads/pdf/bulk_download.html'
        page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")
        user = properties.get('user')
        if user and user != str(AnonymousUser()):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()

        for iid in iids:
            item = MDR._concept.objects.get_subclass(pk=iid)
            if item.can_view(user):
                items.append(item)
        item_querysets = items_for_bulk_download(items, user)

        if title is None:
            if properties.get('title', None):
                title = properties.get('title')
            else:
                title = "Auto-generated document"

        if subtitle is None:
            if properties.get('subtitle', None):
                subtitle = properties.get('subtitle')
            else:
                _list = "<li>" + "</li><li>".join([item.name for item in items if item]) + "</li>"
                subtitle = mark_safe("Generated from the following metadata items:<ul>%s<ul>" % _list)


        debug_as_html = bool(properties.get('debug_as_html'))
        mime_type = 'application/pdf'
        if debug_as_html:
            mime_type = 'text/html'
        PDFDownloader.cache_file(PDFDownloader.get_cache_key(user, iids), (render_to_pdf(
                    template,
                    {
                        'title': title,
                        'subtitle': subtitle,
                        'items': items,
                        'included_items': sorted(
                            [(k, v) for k, v in item_querysets.items()],
                            key=lambda k_v: k_v[0]._meta.model_name
                        ),
                        'pagesize': properties.get('pagesize', page_size),
                    },
                    preamble_template='aristotle_mdr/downloads/pdf/bulk_download_title.html',
                    debug_as_html=debug_as_html
                    ), mime_type, {})
                  )
        return title


def generate_outline_str(bookmarks, indent=0):
    outline_str = ""
    for i, (label, (page, _, _), children) in enumerate(bookmarks, 1):
        outline_str += ('<div>%s %d. %s ..... <span style="float:right"> %d </span> </div>' % (
            '&nbsp;' * indent * 2, i, label.lstrip('0123456789. '), page + 1))
        outline_str += generate_outline_str(children, indent + 1)
    return outline_str


def generate_outline_tree(bookmarks, depth=1):
    return [
        {'label': label, "depth": depth, "page": page + 1, "children": generate_outline_tree(children, depth + 1)}
        for i, (label, (page, _, _), children) in enumerate(bookmarks, 1)
    ]


def render_to_pdf(template_src, context_dict,
                  preamble_template='aristotle_mdr/downloads/pdf/title.html',
                  debug_as_html=False):
    # If the request template doesnt exist, we will give a default one.
    template = select_template([
        template_src,
        'aristotle_mdr/downloads/pdf/managedContent.html'
    ])

    Context(context_dict)
    html = template.render(context_dict)

    if debug_as_html:
        return html

    document = weasyprint.HTML(
        string=template.render(context_dict),
        base_url=PDF_STATIC_PATH
    ).render()

    if not context_dict.get('tableOfContents', False):
        return document.write_pdf()

    generate_outline_str(document.make_bookmark_tree())
    toc = get_template('aristotle_mdr/downloads/pdf/toc.html').render(
        # Context(
        {
            "toc_tree": generate_outline_tree(document.make_bookmark_tree())
        }
        # )
    )

    table_of_contents_document = weasyprint.HTML(
        string=toc,
        base_url=PDF_STATIC_PATH
    ).render()

    if preamble_template:
        title_page = weasyprint.HTML(
            string=get_template(preamble_template).render(context_dict),
            base_url=PDF_STATIC_PATH
        ).render().pages[0]
        document.pages.insert(0, title_page)

    for i, table_of_contents_page in enumerate(table_of_contents_document.pages):
        document.pages.insert(i + 1, table_of_contents_page)

    return document.write_pdf()


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
