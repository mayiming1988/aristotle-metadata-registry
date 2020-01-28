from django.urls import path
from django.utils.translation import ugettext_lazy as _

from aristotle_mdr.contrib.generic.views import (
    GenericAlterOneToManyView,
)

from aristotle_mdr.contrib.links import models, views


urlpatterns = [
    path('relation/<int:iid>/relation/edit/roles/',
         GenericAlterOneToManyView.as_view(
             model_base=models.Relation,
             model_to_add=models.RelationRole,
             model_base_field='relationrole_set',
             model_to_add_field='relation',
             ordering_field='ordinal',
             form_add_another_text=_('Add a role'),
             form_title=_('Change Relation Roles'),
         ), name='relation_roles_edit'),
    path('relation/link/<int:iid>/add/', views.AddLinkWizard.as_view(), name='add_link'),
    path('relation/link/edit/<int:linkid>', views.EditLinkFormView.as_view(), name='edit_link'),
    path('relation/link/json/<int:iid>', views.link_json_for_item, name='link_json_for_item'),
    path('relation/link/remove/<int:linkid>/item/<int:iid>', views.RemoveLinkView.as_view(), name='remove_link')
]
