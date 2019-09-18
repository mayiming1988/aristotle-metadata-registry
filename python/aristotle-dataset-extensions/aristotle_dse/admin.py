from django.contrib import admin
from aristotle_dse import models

from aristotle_mdr.register import register_concept
from aristotle_mdr.search_indexes import SEARCH_CATEGORIES


class DSSDEInclusionInline(admin.TabularInline):
    model=models.DSSDEInclusion
    extra=0
    classes = ('grp-collapse grp-closed', )
    raw_id_fields = ('data_element', )
    autocomplete_lookup_fields = {
        'fk': ['data_element']
    }


class DSSClusterInclusionInline(admin.TabularInline):
    model=models.DSSClusterInclusion
    extra=0
    classes = ('grp-collapse grp-closed', )
    fk_name = 'dss'
    raw_id_fields = ('child', )
    autocomplete_lookup_fields = {
        'fk': ['child']
    }


register_concept(
    models.DataSetSpecification,
    extra_fieldsets=[
        (
            'Methodology',
            {'fields': [
                'statistical_unit',
                'collection_method',
            ]}
        ),
    ],
    extra_inlines=[DSSDEInclusionInline, DSSClusterInclusionInline],
)


register_concept(
    models.DataCatalog,
    search_category=SEARCH_CATEGORIES.data,
    extra_fieldsets=[
        ('Data Source',
            {'fields': ['issued', 'homepage', 'spatial', 'license']}),
    ]
)


register_concept(
    models.Dataset,
    search_category=SEARCH_CATEGORIES.data,
    extra_fieldsets=[
        ('Coverage',
            {'fields': ['spatial', 'temporal']}),
        ('Publishing',
            {'fields': [
                'contact_point', 'landing_page',
                'dct_modified', 'issued', 'frequency'
                ]}),
    ]
)


register_concept(
    models.Distribution,
    search_category=SEARCH_CATEGORIES.data,
    extra_fieldsets=[
        ('File details',
            {'fields': [
                'access_URL', 'download_URL',
                'byte_size', 'media_type', 'format_type',
            ]}),
        ('Publishing',
            {'fields': [
                'license', 'rights',
                'dct_modified', 'issued',
                ]}),
    ],
    reversion={
        'follow': ['distributiondataelementpath_set'],
        'follow_classes': [models.DistributionDataElementPath]
    }
)

# Temporary fix

