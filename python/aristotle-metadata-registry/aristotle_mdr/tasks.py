# Create your tasks here
from __future__ import absolute_import, unicode_literals
from django.contrib.auth.models import User, AnonymousUser
from aristotle_mdr.views import get_if_user_can_view
from aristotle_pdf.downloader import PDFDownloader, render_to_pdf
from aristotle_mdr.utils import get_download_template_path_for_item
from aristotle_mdr import models as MDR
from celery import shared_task
from django.core.cache import cache


class CeleryPDFDownloader(PDFDownloader):
    """
    insert docs here
    """
    @staticmethod
    @shared_task(name='aristotle_mdr.downloader.pdf')
    def async_download(properties, iid):
        """
        create pdf_context and return the results to celery backend.
        :param properties:
        :return:
        """
        user = properties['user']
        user = User.objects.get(email=user) if user is not None else AnonymousUser()
        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)
        template = get_download_template_path_for_item(item, CeleryPDFDownloader.download_type)

        sub_items = [
            (obj_type, qs.visible(user).order_by('name').distinct())
            for obj_type, qs in item.get_download_items()
        ]

        cache.set(iid, {'some_key': 'some value'})

        return iid
