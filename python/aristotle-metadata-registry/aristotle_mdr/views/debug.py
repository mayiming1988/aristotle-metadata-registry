from django.http import HttpResponse, Http404


def download(request):
    """Built in download method"""
    from aristotle_mdr.contrib.aristotle_pdf.downloader import PDFDownloader
    from django.conf import settings

    default_options = {
        'include_supporting': True,
        'include_related': True,
        'subclasses': None,
        'front_page': None,
        'back_page': None,
        'email_copy': False
    }

    maker = PDFDownloader(
        item_ids=[request.GET.get('iid')],
        user_id=request.user.pk,
        options=default_options
    )

    output = maker.create_file()

    response = HttpResponse(output, content_type='application/pdf')
    return response
