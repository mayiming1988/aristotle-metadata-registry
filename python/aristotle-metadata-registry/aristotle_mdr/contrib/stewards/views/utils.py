from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.groups.backends import (
    GroupURLManager, GroupMixin,
    HasRoleMixin, HasRolePermissionMixin,
)

class StewardGroupMixin(GroupMixin):
    group_class = MDR.StewardOrganisation

