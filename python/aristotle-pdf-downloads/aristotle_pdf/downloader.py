from aristotle_mdr.utils import get_download_template_path_for_item, downloads as download_utils
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr import models as MDR

import os

from django.conf import settings
from django.http import HttpResponse, Http404
from django.template.loader import select_template, get_template
from django.template import Context
from django.utils.safestring import mark_safe
from django.core.cache import cache
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

    def get_download_config(self) -> Dict[str, Any]:
        """
        Create configuration for pdf download method
        :param request: request object
        :param iid: id of the item requested
        :return: properties for item, id of the item
        """
        # page size for the pdf
        page_size = getattr(settings, 'PDF_PAGE_SIZE', "A4")

        item = self.items[0]
        sub_items = [
            (obj_type, qs.visible(user).order_by('name').distinct())
            for obj_type, qs in item.get_download_items()
        ]

        context = {
            'user': None,
            'page_size': settings.PDF_PAGE_SIZE,
            'title': self.item.name,
            'subitems': sub_items,
            'tableOfContents': len(sub_items) > 0,
        }

        return context

    def get_bulk_download_config(self) -> Dict[str, Any]:
        """
        generate properties for pdf document
        :param request: API request object
        :param items: items to download
        :return: properties computed, items
        """

        _list = "<li>" + "</li><li>".join([item.name for item in items if item]) + "</li>"
        subtitle = mark_safe("Generated from the following metadata items:<ul>%s<ul>" % _list)

        item_querysets = items_for_bulk_download(items, user)

        properties = {
            'user': str(self.user),
            'title': 'Auto-generated document',
            'subtitle': subtitle,
            'debug_as_html': False,
            'page_size': settings.PDF_PAGE_SIZE,
            'items': self.items,
            'included_items': sorted(
                [(k, v) for k, v in item_querysets.items()],
                key=lambda k_v: k_v[0]._meta.model_name
            ),
        }
        return properties

    def download(self):
        if self.bulk:
            context = self.get_bulk_download_config()
            template = 'aristotle_mdr/downloads/pdf/bulk_download.html'
        else:
            template = get_download_template_path_for_item(item, self.download_type)
            context = self.get_download_config()

        return render_to_pdf(template, context)


def generate_outline_str(bookmarks, indent=0):
    outline_str = ""
    for i, (label, (page, _, _), children) in enumerate(bookmarks, 1):
        outline_str += ('<div>%s %d. %s ..... <span style="float:right"> %d </span> </div>' % (
            '&nbsp;' * indent * 2, i, label.lstrip('0123456789. '), page + 1))
        outline_str += generate_outline_str(children, indent + 1)
    return outline_str


def generate_outline_tree(bookmarks, depth=1):
    outline_str = []
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

    context = Context(context_dict)
    html = template.render(context_dict)

    if debug_as_html:
        return html

    document = weasyprint.HTML(
        string=template.render(context_dict),
        base_url=PDF_STATIC_PATH
    ).render()

    if not context_dict.get('tableOfContents', False):
        return document.write_pdf()

    table_of_contents_string = generate_outline_str(document.make_bookmark_tree())
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
