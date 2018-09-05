from django.shortcuts import get_object_or_404, redirect
from aristotle_mdr.utils import url_slugify_concept
from django.contrib.auth.decorators import login_required
from aristotle_mdr.models import _concept
from aristotle_mdr.perms import user_can_view
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http.response import JsonResponse


class ToggleFavourite(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        itemid = self.kwargs['iid']
        item = get_object_or_404(_concept, pk=itemid).item

        if not user_can_view(request.user, item):
            raise PermissionDenied

        favourited = request.user.profile.toggleFavourite(item)

        if request.is_ajax():
            return self.get_json_response(favourited)
        else:
            return self.redirect_with_message(item, favourited)

    def get_message(self, item, favourited):
        if self.request.GET.get('next', None):
            return redirect(request.GET.get('next'))

        if favourited:
            message = _("%s added to favourites.") % (item.name)
        else:
            message = _("%s removed from favourites.") % (item.name)

        message = _(message + " Review your favourites from the user menu.")
        return message

    def redirect_with_message(self, item, favourited):
        message = self.get_message(item, favourited)
        messages.add_message(self.request, messages.SUCCESS, message)
        return redirect(url_slugify_concept(item))

    def get_json_response(self, item, favourited):
        message = self.get_message(item, favourited)
        response_dict = {
            'success': True,
            'message': message,
            'favourited': favourited
        }
        return JsonResponse(response_dict)
