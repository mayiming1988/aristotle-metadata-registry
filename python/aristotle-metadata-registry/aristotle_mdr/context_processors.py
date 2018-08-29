from aristotle_mdr.utils import fetch_aristotle_settings
from aristotle_mdr.views.bulk_actions import get_bulk_actions
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth import get_user_model


# This allows us to pass the Aristotle settings through to the final rendered page
def settings(request):
    return {
        "config": fetch_aristotle_settings(),
        'bulk_actions': get_bulk_actions(),
    }

def auth(request):
    """
    Replacement for the django auth context processor, with some prefetching for aristotle
    Adapted from the original at django.contrib.auth.context_processors
    """
    if hasattr(request, 'user'):
        user = get_user_model().objects.filter(pk=request.user.pk).select_related('profile').first()
    else:
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()

    return {
        'user': user,
        'perms': PermWrapper(user),
    }
