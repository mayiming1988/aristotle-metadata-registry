from django.db import models
from aristotle_mdr import concept


class ClassificationScheme(concept):

    classificationStructure = models.TextField()
