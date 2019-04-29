from django.db import models
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet


class FrameworkDimensionQuerySet(TreeQuerySet):
    pass


class FrameworkDimensionManager(models.Manager.from_queryset(FrameworkDimensionQuerySet), TreeManager):
    pass
