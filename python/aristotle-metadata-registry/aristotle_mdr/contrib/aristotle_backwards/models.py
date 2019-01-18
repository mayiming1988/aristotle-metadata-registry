from django.db import models
from aristotle_mdr.models import concept


class ClassificationScheme(concept):
    """
    The descriptive information for an arrangement or division of objects into groups
    based on characteristics, which the objects have in common
    """

    classificationStructure = models.TextField(
        blank=True
    )
