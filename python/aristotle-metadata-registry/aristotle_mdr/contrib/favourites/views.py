from django.shortcuts import get_object_or_404, redirect
from aristotle_mdr.utils import url_slugify_concept
from django.contrib.auth.decorators import login_required
from aristotle_mdr.models import _concept
from aristotle_mdr.perms import user_can_view
from django.utils.translation import ugettext_lazy as _

@login_required
def toggleFavourite(request, iid):
    item = get_object_or_404(_concept, pk=iid).item
    if not user_can_view(request.user, item):
        raise PermissionDenied

    request.user.profile.toggleFavourite(item)

    if request.GET.get('next', None):
        return redirect(request.GET.get('next'))

    #if item.concept in request.user.profile.favourites.all():
    #    message = _("%s added to favourites.") % (item.name)
    #else:
    #    message = _("%s removed from favourites.") % (item.name)

    #message = _(message + " Review your favourites from the user menu.")
    #messages.add_message(request, messages.SUCCESS, message)
    return redirect(url_slugify_concept(item))
