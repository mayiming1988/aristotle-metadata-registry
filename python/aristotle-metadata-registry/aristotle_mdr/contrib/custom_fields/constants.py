from model_utils import Choices
from django.utils.translation import ugettext_lazy as _

# The Status of a Custom Field.
#
# Active = This field can be added or edited for items in the system
#
# Inactive = This field is no longer editable or addable to metadata items
# by regular users. Superusers can alter content. Older items
# with this field will still display it.
#
# Hidden = This field is no longer editable or addable to metadata items by regular users.
# Superusers can alter content. Older items with this field will not
# display it.

CUSTOM_FIELD_STATES = Choices(
    (0, 'active', _('Active & Visible')),
    (1, 'inactive', _('Inactive & Visible')),
    (2, 'hidden', _('Inactive & Hidden'))
)
