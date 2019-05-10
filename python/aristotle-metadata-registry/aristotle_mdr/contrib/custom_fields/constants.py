from model_utils import Choices
from django.utils.translation import ugettext_lazy as _


CUSTOM_FIELD_STATES = Choices(
    (0, 'active', _('Active & Visible')),
    (1, 'inactive', _('Inactive & Visible')),
    (2, 'hidden', _('Inactive & Hidden'))
)
