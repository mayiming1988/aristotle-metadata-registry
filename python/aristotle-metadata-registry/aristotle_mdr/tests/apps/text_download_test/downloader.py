from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import select_template
from django.template import Context
from django.contrib.auth.models import AnonymousUser
from aristotle_mdr import models as MDR
from django.contrib.auth import get_user_model
from django.core.cache import cache

from celery import shared_task

from aristotle_mdr.downloader import items_for_bulk_download, Downloader
from aristotle_mdr.views import get_if_user_can_view


class TestTextDownloader(Downloader):
    download_type = "txt"
    metadata_register = '__all__'
    label = "Text"
    icon_class = "fa-file-o"
    description = "Test Downloader"

    @classmethod
    def get_download_config(cls, request, item):
        properties = {
            'user': None
        }
        user = getattr(request, 'user', None)
        if user:
            properties['user'] = str(user)
        return properties

    @staticmethod
    @shared_task(name='aristotle_mdr.tests.apps.text_download_test.downloader.download')
    def download(properties, iid):
        User = get_user_model()
        user = properties['user']
        if user and user != str(AnonymousUser):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()

        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)

        template = get_download_template_path_for_item(item, TestTextDownloader.download_type)

        template = select_template([template])
        context = {'item': item}
        txt = template.render(context)
        TestTextDownloader.cache_file(TestTextDownloader.get_cache_key(user, iid), (txt, 'text/plain', {}))
        return item

    @classmethod
    def get_bulk_download_config(cls, request, items):
        """
        creates a dict of properties required to generate bulk_downloads
        :param request: request object from the client
        :param items: items to download
        :return: The set of properties required by bulk_download method
        """
        out = []
        user = getattr(request, 'user', None)
        if request.GET.get('title', None):
            out.append(request.GET.get('title'))
        else:
            out.append("Auto-generated document")

        properties = {
            'out': out,
            'user': None,
            'title': out[0] or 'Auto-generated document'
        }
        if user:
            properties['user'] = str(user)
        return properties

    @staticmethod
    @shared_task(name='aristotle_mdr.tests.apps.text_download_test.downloader.bulk_download')
    def bulk_download(properties, iids):
        items = []

        out = properties.get('out', [])
        # Getting user from the available email data
        User = get_user_model()
        user = properties.get('user', None)
        if user and user != str(AnonymousUser()):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()
        for iid in iids:
            item = MDR._concept.objects.get_subclass(pk=iid)
            if item.can_view(user):
                items.append(item)
        item_querysets = items_for_bulk_download(items, user)

        for model, details in item_querysets.items():
            out.append(model.get_verbose_name())
            for item in details['qs']:
                template = select_template([
                    get_download_template_path_for_item(item, TestTextDownloader.download_type, subpath="inline"),
                ])
                context = {
                    'item': item,
                }
                out.append(template.render(context))
        TestTextDownloader.cache_file(TestTextDownloader.get_cache_key(user, iids), ("\n\n".join(out), 'text/plain', {}))

        return True
