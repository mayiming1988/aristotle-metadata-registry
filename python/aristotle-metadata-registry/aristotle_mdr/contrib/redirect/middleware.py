from aristotle_mdr.contrib.redirect.exceptions import Redirect
from django.http import HttpResponseRedirect

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class RedirectMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)
        return response

    def process_exception(self, request, e):
        if isinstance(e, Redirect):
            return HttpResponseRedirect(e.url)
        return None
