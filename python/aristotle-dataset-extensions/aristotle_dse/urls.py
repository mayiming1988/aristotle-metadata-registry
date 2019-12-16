from django.urls import path, include
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _


from aristotle_dse import views, models
from aristotle_dse.views import DatasetSpecificationView

from aristotle_mdr.contrib.generic.views import (
    GenericAlterOneToManyView,
    GenericAlterManyToManyView,
)

urlpatterns = [
    path('item/<int:iid>/datasetspecification/<slug:name_slug>/', DatasetSpecificationView.as_view(), name='datasetspecification'),

    path('dse/',  include([

        path('remove/deFromDss/<int:de_id>/<int:dss_id>', views.RemoveDEFromDSS.as_view(), name='removeDataElementFromDSS'),
        path('remove/clusterFromDss/<int:cluster_id>/<int:dss_id>', views.RemoveClusterFromDSS.as_view(), name='removeClusterFromDSS'),

        path('add/deToDss/<int:dss_id>', views.addDataElementsToDSS, name='addDataElementsToDSS'),
        path('add/clustersToDss/<int:dss_id>', views.addClustersToDSS, name='addClustersToDSS'),

        path('dss/edit_de_inclusion/<int:dss_id>/<int:de_id>', views.editDataElementInclusion, name='editDEInclusion'),
        path('dss/edit_cluster_inclusion/<int:dss_id>/<int:cluster_id>', views.editClusterInclusion, name='editDSSInclusion'),
        path('dss/reorder_inclusion/<int:dss_id>/<str:inc_type>', views.editInclusionOrder, name='editInclusionOrder'),

        # These are required for about pages to work. Include them, or custom items will die!
        path('about/<path:template>/', views.DynamicTemplateView.as_view(), name="about"),
        path('about/', TemplateView.as_view(template_name='aristotle_dse/static/about_aristotle_dse.html'), name="about"),

        path('add/column_to_distribution/<int:iid>/',
             GenericAlterOneToManyView.as_view(
                 model_base=models.Distribution,
                 model_to_add=models.DistributionDataElementPath,
                 model_base_field='distributiondataelementpath_set',
                 model_to_add_field='distribution',
                 ordering_field='order',
                 form_add_another_text=_('Add a column'),
                 form_title=_('Change Columns')
             ), name='add_column_to_distribution'),

        path('add/dataset_to_catalog/<int:iid>/',
             GenericAlterManyToManyView.as_view(
                 model_base=models.DataCatalog,
                 model_to_add=models.Dataset,
                 model_base_field='dataset_set',
                 form_title=_('Change Datasets')
             ), name='add_dataset_to_catalog'),

        ])
    )
]
