import os
from io import BytesIO

from django.template.loader import select_template, get_template
from django.core.files.base import File

from aristotle_mdr.contrib.help.models import ConceptHelp
from aristotle_mdr.downloader import HTMLDownloader

import logging
import weasyprint
from PyPDF2 import PdfFileMerger

PDF_STATIC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pdf_static')

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class PDFDownloader(HTMLDownloader):
    download_type = "pdf"
    file_extension = 'pdf'
    metadata_register = '__template__'
    label = "PDF"
    icon_class = "fa-file-pdf-o"
    description = "Downloads for various content types in the PDF format"
    allow_wrapper_pages = True

    def wrap_file(self, generated_bytes) -> BytesIO:
        if self.has_wrap_pages:
            merger = PdfFileMerger()
            pages = self.get_wrap_pages()
            pages.insert(1, generated_bytes)
            for page_bytes in pages:
                if page_bytes is not None:
                    merger.append(BytesIO(page_bytes))
            final_file = BytesIO()
            merger.write(final_file)
            merger.close()  # Close all files given to the merger
            return final_file
        else:
            return BytesIO(generated_bytes)

    def create_file(self):
        template = self.get_template()
        context = self.get_context()

        byte_string = render_to_pdf(template, context)
        final_file = self.wrap_file(byte_string)
        return File(final_file)


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
                  debug_as_html=False) -> bytes:
    # If the request template doesnt exist, we will give a default one.
    template = select_template([
        template_src,
        'aristotle_mdr/downloads/html/managedContent.html'
    ])

    html = template.render(context_dict)

    if debug_as_html:
        return html

    document = weasyprint.HTML(
        string=template.render(context_dict),
        base_url=PDF_STATIC_PATH
    ).render()

    if not context_dict.get('tableOfContents', False):
        return document.write_pdf()

    toc = get_template('aristotle_mdr/downloads/html/toc.html').render(
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
