from typing import List, Optional, Any
from django.urls import reverse
from django.utils.html import format_html

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

    empty_text = 'None'
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
                url = self.url
                # Get a nice name for object
                name: str
                if hasattr(self.obj, 'name'):
                    name = self.obj.name
                else:
                    name = str(self.obj)

                if url:
                    # Build link
                    return format_html(
                        '<a href="{url}">{name}</a> <span class="text-danger">*</span>',
                        url=url,
                        name=name
                    )

                else:
                    # Return plain name
                    return name
            else:
                # If field is set but object is None no perm
                return self.perm_message
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
    def heading(self):
        # Pluralize names for grouped field
        if self.fname and self.fname[-1] != 's':
            return self.fname + 's'
        return self.fname

    @property
    def headings(self) -> List[str]:
        headings = []
        if self.sub_fields:
            for field in self.sub_fields[0]:
                headings.append(field.heading)
        return headings

    def __str__(self):
        # Get str of sub fields
        sub_strings = [str(f) for f in self.sub_fields]
        result = ', '.join(sub_strings)

        if result:
            # Result can contain html links along with user data
            # so bleaching is required here
            return bleach_filter(result)

        return self.empty_text
