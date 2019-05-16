from aristotle_mdr.models import concept
from ckeditor_uploader.fields import RichTextUploadingField as RichTextField
from aristotle_mdr.utils.model_utils import ManagedItem


class ClassificationScheme(concept):
    """
    3.3.9 (edition 2) Classification Scheme

    The descriptive information for an arrangement or division of objects into groups
    based on characteristics, which the objects have in common
    """

    classificationStructure = RichTextField(
        blank=True
    )


class RepresentationClass(ManagedItem):
    """
    4.13.1.4 (edition 2) Representation Class

    Representation Class is the Classification Scheme for representation.
    The set of classes make it easy to distinguish among the elements in the registry.
    For instance, a data element categorized with the representation class 'amount' is
    different from an element categorized as 'number'.

    It probably won't make sense to compare the contents of these elements, or
    perform calculations using them together.
    """
    template = "aristotle_mdr_backwards/manageditems/representationclass.html"

