from django.db import models
from aristotle_mdr.models import concept


class ClassificationScheme(concept):

    classificationStructure = models.TextField()
