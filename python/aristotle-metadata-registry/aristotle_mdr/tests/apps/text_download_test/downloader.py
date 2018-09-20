from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import select_template
from django.template import Context
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.core.cache import cache

from celery import shared_task

from aristotle_mdr.utils import get_download_template_path_for_item, downloads as download_utils
from aristotle_mdr.downloader import items_for_bulk_download, DownloaderBase


class TestTextDownloader(DownloaderBase):
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
        return properties, item

    @staticmethod
    @shared_task
    def download(properties, item):
        User = get_user_model()
        template = get_download_template_path_for_item(item, TestTextDownloader.download_type)
        user = properties['user']
        if user and user != str(AnonymousUser):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()

        template = select_template([template])
        context = Context({'item': item})
        txt = template.render(context)
        cache.set(download_utils.get_download_cache_key(item, user), (txt, 'text/plain'))
        return True

    @classmethod
    def get_bulk_download_config(cls, request, items):
        out = []
        user = getattr(request, 'user', None)
        if request.GET.get('title', None):
            out.append(request.GET.get('title'))
        else:
            out.append("Auto-generated document")

        properties = {
            'out': out,
            'user': None
        }
        if user:
            properties['user'] = str(user)
        return properties, items

    @staticmethod
    @shared_task
    def bulk_download(properties, items):
        out = properties.get('out', [])
        # Getting user from the available email data
        User = get_user_model()
        user = properties.get('user', None)
        if user and user != str(AnonymousUser()):
            user = User.objects.get(email=user)
        else:
            user = AnonymousUser()

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

        cache.set(download_utils.get_download_cache_key(item, user), ("\n\n".join(out), 'text/plain'))

        return True