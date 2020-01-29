from django.http import HttpResponse
import pypandoc
from aristotle_mdr.downloader import PandocDownloader


class PandocHTMLDownloader(PandocDownloader):
    metadata_register = '__all__'

    def convert_html(self, html):
        return pypandoc.convert_text(html, 'html', format='html', return_bytes=True)


def download(request, dtype):
    """Built in download method"""
    from aristotle_mdr.contrib.aristotle_pdf.downloader import PDFDownloader, PythonPDFDownloader
    from aristotle_mdr.downloader import DocxDownloader
    from aristotle_mdr.downloader import HTMLDownloader

    if dtype == "pdf":
        DClass = PDFDownloader
    elif dtype == "word":
        DClass = DocxDownloader
    elif dtype == "html":
        DClass = HTMLDownloader
    elif dtype == "pandochtml":
        DClass = PandocHTMLDownloader
    elif dtype == "slow":
        DClass = PythonPDFDownloader

    default_options = {
        'include_supporting': bool(request.GET.get('sup')),
        'include_related': bool(request.GET.get('rel')),
        'subclasses': None,
        'front_page': None,
        'back_page': None,
        'email_copy': False,
        "CURRENT_HOST": request.scheme + "://" +request.get_host(),
    }

    item_list = request.GET.getlist('iid')

    if bool(request.GET.get('pub')):
        user_id = None
    else:
        user_id = request.user.pk

    maker = DClass(
        item_ids=item_list,
        user_id=user_id,
        options=default_options,
        override_bulk=len(item_list)>1 or bool(request.GET.get('bulk')),
    )

    output = maker.create_file()

    response = HttpResponse(output, content_type=DClass.mime_type)
    filename = "download.{}".format(DClass.file_extension)
    if DClass.file_extension != "html":
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response
