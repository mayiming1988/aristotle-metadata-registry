from typing import List, Optional, Any
from django.urls import reverse

from aristotle_mdr.templatetags.util_tags import bleach_filter
from aristotle_mdr.models import _concept


class VersionField:
    """
    Field for use in previous version display
    Template to render in helpers/version_field.html
    """

    empty_text: str = 'None'
    link: bool = False
    group: bool = False

    def __init__(self, fname: str, value, html=False):
        self.fname = fname
        self.value = str(value)
        self.html = html

    @property
    def is_link(self):
        return self.link

    @property
    def is_group(self):
        return self.group

    @property
    def is_html(self):
        return self.html

    @property
    def heading(self):
        return self.fname

    def __str__(self):
        raw = self.value

        if not raw:
            raw = self.empty_text

        if self.html:
            # Automatically bleach result if html
            return bleach_filter(raw)
        return raw


class VersionLinkField(VersionField):
    """Version field that links to a concept"""

    empty_text = ''
    perm_message = 'Linked to object you do not have permission to view'

    link = True
    group = False
    html = False

    def __init__(self, fname: str, id: Optional[int], obj: Optional[Any]):
        self.fname = fname
        self.id = id
        self.obj = obj

        self.is_concept = isinstance(obj, _concept)

    @property
    def url(self):
        if self.obj and self.is_concept:
            return reverse('aristotle:item', args=[self.obj.id])
        return ''

    def __str__(self):
        if self.id is not None:
            if self.obj:
                # Get a nice name for object
                if hasattr(self.obj, 'name'):
                    return self.obj.name
                return str(self.obj)
            else:
                # If field is set but object is None no perm
                self.value = self.perm_message
        # Empty value if no id
        return self.empty_text


class VersionGroupField(VersionField):
    """Field with groups of subfields"""

    empty_text = 'Empty'
    link = False
    group = True
    html = False

    def __init__(self, fname: str, sub_fields: List[List[VersionField]]):
        self.fname = fname
        self.sub_fields = sub_fields

    @property
    def headings(self) -> List[str]:
        headings = []
        if self.sub_fields:
            for field in self.sub_fields[0]:
                headings.append(field.heading)
        return headings

    def __str__(self):
        return '{} sub items'.format(len(self.sub_fields))
