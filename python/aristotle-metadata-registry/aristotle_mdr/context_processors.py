from aristotle_mdr.utils import fetch_aristotle_settings
from aristotle_mdr.views.bulk_actions import get_bulk_actions
from aristotle_mdr.models import PossumProfile
from django.utils.functional import SimpleLazyObject


# This allows us to pass the Aristotle settings through to the final rendered page
def settings(request):
    return {
        "config": SimpleLazyObject(fetch_aristotle_settings),
        'bulk_actions': SimpleLazyObject(get_bulk_actions),
    }


def get_profile(request):
    return PossumProfile.objects.get(user=request.user)


def profile(request):
    """
    Context processor providing lazy profile object
    Not currently used
    """

    lazy_profile = SimpleLazyObject(lambda: get_profile(request))

    return {
        'profile': lazy_profile
    }
