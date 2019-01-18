from aristotle_mdr.models import concept
from ckeditor_uploader.fields import RichTextUploadingField as RichTextField


class ClassificationScheme(concept):
    """
    The descriptive information for an arrangement or division of objects into groups
    based on characteristics, which the objects have in common
    """

    classificationStructure = RichTextField(
        blank=True
    )
