from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

REVIEW_STATES = Choices(
    (0, 'open', _('Open')),
    (5, 'revoked', _('Revoked')),
    (10, 'approved', _('Approved')),
    (15, 'closed', _('Closed')),
)
