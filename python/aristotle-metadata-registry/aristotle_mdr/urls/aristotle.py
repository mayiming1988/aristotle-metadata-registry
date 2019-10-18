from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

from haystack.views import search_view_factory

import aristotle_mdr.views as views
from aristotle_mdr.views.search import PermissionSearchView
import aristotle_mdr.forms as forms
import aristotle_mdr.models as models
from aristotle_mdr.contrib.generic.views import (
    GenericAlterOneToManyView,
    generic_foreign_key_factory_view
)

from django.utils.translation import ugettext_lazy as _

urlpatterns = [
    path('', views.SmartRoot.as_view(
        unauthenticated_pattern='aristotle_mdr:home',
        authenticated_pattern='aristotle_mdr:userHome'
    ), name='smart_root'),
    path('home/', TemplateView.as_view(template_name='aristotle_mdr/static/home.html'), name="home"),
    path('manifest.json', TemplateView.as_view(template_name='meta/manifest.json', content_type='application/json')),
    path('robots.txt', TemplateView.as_view(template_name='meta/robots.txt', content_type='text/plain')),
    path('sitemap.xml', views.sitemaps.main, name='sitemap_xml'),
    path('sitemaps/sitemap_<int:page>.xml$', views.sitemaps.page_range, name='sitemap_range_xml'),

    path('steward', include(('aristotle_mdr.contrib.stewards.urls', 'aristotle_mdr.contrib.stewards'), namespace='stewards')),

    # all the below take on the same form:
    # all the below take on the same form:
    # path(r'^itemType/(?P<iid>\d+)?/?
    # Allowing for a blank ItemId (iid) allows aristotle to redirect to /about/itemtype instead of 404ing

    path('conceptualdomain/<int:iid>?/edit/values/',
        GenericAlterOneToManyView.as_view(
            model_base=models.ConceptualDomain,
            model_to_add=models.ValueMeaning,
            model_base_field='valuemeaning_set',
            model_to_add_field='conceptual_domain',
            ordering_field='order',
            form_add_another_text=_('Add a value meaning'),
            form_title=_('Change Value Meanings')
        ), name='value_meanings_edit'),

    path('item/<int:iid>?/alter_relationship/<slug:fk_field>/',
        generic_foreign_key_factory_view,
        name='generic_foreign_key_editor'),

    re_path(r'^workgroup/(?P<iid>\d+)(?:-(?P<name_slug>[A-Za-z0-9\-_]+))?/?$', views.workgroups.WorkgroupView.as_view(), name='workgroup'),
    path('workgroup/<int:iid>/members/', views.workgroups.MembersView.as_view(), name='workgroupMembers'),
    path('workgroup/<int:iid>/items/', views.workgroups.ItemsView.as_view(), name='workgroupItems'),
    path('workgroup/<int:iid>/leave/', views.workgroups.LeaveView.as_view(), name='workgroup_leave'),
    path('workgroup/<int:iid>/add_member', views.workgroups.AddMembersView.as_view(), name='addWorkgroupMembers'),
    path('workgroup/<int:iid>/change_roles/<int:user_pk>/', views.workgroups.ChangeUserRoles.as_view(), name='workgroup_member_change_role'),
    path('workgroup/<int:iid>/remove/<int:user_pk>/', views.workgroups.RemoveUser.as_view(), name='workgroup_member_remove'),
    path('workgroup/<int:iid>/archive/', views.workgroups.ArchiveView.as_view(), name='archive_workgroup'),
    path('workgroup/<int:iid>/edit', views.workgroups.EditWorkgroup.as_view(), name='workgroup_edit'),
    path('workgroups/create/', views.workgroups.CreateWorkgroup.as_view(), name='workgroup_create'),
    path('workgroups/all/', views.workgroups.ListWorkgroup.as_view(), name='workgroup_list'),

    path('discussions/', views.discussions.All.as_view(), name='discussions'),
    path('discussions/new/', views.discussions.New.as_view(), name='discussionsNew'),
    path('discussions/workgroup/<int:wgid>/', views.discussions.Workgroup.as_view(), name='discussionsWorkgroup'),
    path('discussions/post/<int:pid>/', views.discussions.Post.as_view(), name='discussionsPost'),
    path('discussions/post/<int:pid>/newcomment/', views.discussions.NewComment.as_view(), name='discussionsPostNewComment'),
    path('discussions/delete/comment/<int:cid>/', views.discussions.DeleteComment.as_view(), name='discussionsDeleteComment'),
    path('discussions/delete/post/<int:pid>/', views.discussions.DeletePost.as_view(), name='discussionsDeletePost'),
    path('discussions/edit/comment/<int:cid>/', views.discussions.EditComment.as_view(), name='discussionsEditComment'),
    path('discussions/edit/post/<int:pid>/', views.discussions.EditPost.as_view(), name='discussionsEditPost'),
    path(r'^discussions/post/(?P<pid>\d+)/toggle/?$', views.discussions.TogglePost.as_view(), name='discussionsPostToggle'),

    path(r'^item/(?P<iid>\d+)/edit/?$', views.editors.EditItemView.as_view(), name='edit_item'),
    path(r'^item/(?P<iid>\d+)/clone/?$', views.editors.CloneItemView.as_view(), name='clone_item'),
    path(r'^item/(?P<iid>\d+)/graphs/?$', views.tools.ItemGraphView.as_view(), name='item_graphs'),
    path(r'^item/(?P<iid>\d+)/related/(?P<relation>.+)?$', views.tools.ConceptRelatedListView.as_view(), name='item_related'),
    path(r'^item/(?P<iid>\d+)/compare_fields/?$', views.versions.CompareHTMLFieldsView.as_view(), name='compare_fields'),
    path(r'^item/(?P<iid>\d+)/history/$', views.versions.ConceptVersionListView.as_view(), name='item_history'),
    path(r'^item/(?P<iid>\d+)/compare/?$', views.versions.ConceptVersionCompareView.as_view(), name='compare_versions'),
    path(r'^item/(?P<iid>\d+)/registrationHistory/?$', views.registration_history, name='registrationHistory'),
    path(r'^item/(?P<iid>\d+)/child_states/?$', views.actions.CheckCascadedStates.as_view(), name='check_cascaded_states'),

    # Concept page overrides
    path(r'^item/(?P<iid>\d+)/dataelement/(?P<name_slug>.+)/?$', views.DataElementView.as_view(), name='dataelement'),
    path(r'^item/(?P<iid>\d+)/objectclass/(?P<name_slug>.+)/?$', views.ObjectClassView.as_view(), name='objectclass_view'),
    path(r'^item/(?P<iid>\d+)(?:/(?P<model_slug>\w+)/(?P<name_slug>.+))?/?$', views.ConceptView.as_view(), name='item'),
    path(r'^item/(?P<iid>\d+)(?:/.*)?$', views.ConceptView.as_view(), name='item_short'),  # Catch every other 'item' URL and throw it for a redirect
    path(r'^item/(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?(.*)?$', views.concept_by_uuid, name='item_uuid'),

    path(r'^unmanaged/measure/(?P<iid>\d+)(?:/(?P<model_slug>\w+)/(?P<name_slug>.+))?/?$', views.MeasureView.as_view(), name='measure'),
    path(r"^managed_items/(?P<model_slug>.+)/(?P<iid>.+)?$", view=views.ManagedItemView.as_view(), name="view_managed_item"),

    # path(r'^create/?$', views.item, name='item'),
    path(r'^create/?$', views.create_list, name='create_list'),
    path(r'^create/wizard/aristotle_mdr/dataelementconcept$', views.wizards.DataElementConceptWizard.as_view(), name='createDataElementConcept'),
    path(r'^create/wizard/aristotle_mdr/dataelement$', views.wizards.DataElementWizard.as_view(), name='createDataElement'),
    path(r'^create/(?P<app_label>.+)/(?P<model_name>.+)/?$', views.wizards.create_item, name='createItem'),
    path(r'^create/(?P<model_name>.+)/?$', views.wizards.create_item, name='createItem'),

    path(r'^download/options/(?P<download_type>\w+)/?$', views.downloads.DownloadOptionsView.as_view(), name='download_options'),
    path(r'^download/bulk/(?P<download_type>\w+)/?$', views.downloads.BulkDownloadView.as_view(), name='bulk_download'),
    path(r'^download/(?P<download_type>\w+)/(?P<iid>\d+)/?$', views.downloads.DownloadView.as_view(), name='download'),
    path(r'^dlstatus/(?P<taskid>[a-z0-9\-]+)/?$',
        views.downloads.DownloadStatusView.as_view(),
        name='download_status',
        ),

    path(r'^action/supersede/(?P<iid>\d+)$', views.actions.SupersedeItemView.as_view(), name='supersede'),
    path(r'^action/proposed/supersede/(?P<iid>\d+)$', views.actions.ProposedSupersedeItemView.as_view(), name='proposed_supersede'),

    path(r'^action/bulkaction/?$', views.bulk_actions.BulkAction.as_view(), name='bulk_action'),
    path(r'^action/bulkaction/state/?$', views.bulk_actions.ChangeStatusBulkActionView.as_view(), name='change_state_bulk_action'),
    path(r'^action/changestatus/(?P<iid>\d+)$', views.ChangeStatusView.as_view(), name='changeStatus'),
    path(r'^toolbox/compare/?$', views.comparator.MetadataComparison.as_view(), name='compare_concepts'),
    path(r'^toolbox/dataelementcomponents/?$', views.tools.DataElementsAndSubcomponentsStatusCheckTool.as_view(), name='data_element_components_tool'),

    path(r'^status/delete/(?P<sid>\d+)/item/(?P<iid>\d+)$', views.DeleteStatus.as_view(), name='deleteStatus'),
    path(r'^status/edit/(?P<sid>\d+)/item/(?P<iid>\d+)/registrationauthority/(?P<raid>\w+)$', views.EditStatus.as_view(), name='editStatus'),
    path(r'^status/history/(?P<sid>\d+)/item/(?P<iid>\d+)/registrationauthority/(?P<raid>\w+)$', views.StatusHistory.as_view(), name='statusHistory'),

    path(r'^account/?$', RedirectView.as_view(url=reverse_lazy("aristotle:userHome"), permanent=True)),
    path(r'^account/home/?$', views.user_pages.home, name='userHome'),
    path(r'^account/sandbox/?$', views.user_pages.SandboxedItemsView.as_view(), name='userSandbox'),
    path(r'^account/sandbox/delete/?$', views.actions.DeleteSandboxView.as_view(), name="sandbox_delete"),
    path(r'^account/roles/?$', views.user_pages.Roles.as_view(), name='userRoles'),
    path(r'^account/admin/?$', views.user_pages.admin_tools, name='userAdminTools'),
    path(r'^account/admin/statistics/?$', views.user_pages.admin_stats, name='userAdminStats'),
    path(r'^account/edit/?$', views.user_pages.EditView.as_view(), name='userEdit'),
    path(r'^account/notificationpermissions/?$', views.user_pages.NotificationPermissions.as_view(), name='notificationPermissions'),
    path(r'^account/profile/?$', views.user_pages.ProfileView.as_view(), name='userProfile'),
    path(r'^account/recent/?$', views.user_pages.recent, name='userRecentItems'),
    path(r'^account/workgroups/?$', views.user_pages.MyWorkgroupList.as_view(), name='userWorkgroups'),
    path(r'^account/workgroups/archives/?$', views.user_pages.WorkgroupArchiveList.as_view(), name='user_workgroups_archives'),
    path(r'^account/notifications/?$', views.user_pages.InboxView.as_view(), name='userInbox'),
    path(r'^account/notifications-all/?$', views.user_pages.InboxViewAll.as_view(), name='userInboxAll'),
    path(r'^account/notifications/api/mark-all-as-read/', views.notify.MarkAllReadApiView.as_view(), name='api_mark_all_read'),

    path(r'^account/django/(.*)?$', views.user_pages.django_admin_wrapper, name='django_admin'),

    path(r'^account/registrartools/?$', views.user_pages.RegistrarTools.as_view(), name='userRegistrarTools'),

    path(r'^registrationauthority/create/?$', views.registrationauthority.CreateRegistrationAuthority.as_view(), name='registrationauthority_create'),
    path(r'^account/admin/registrationauthority/all/?$', views.registrationauthority.ListRegistrationAuthorityAll.as_view(), name='registrationauthority_list'),

    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/data_dictionary$', views.registrationauthority.DateFilterView.as_view(), name='registrationauthority_data_dictionary'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/data_dictionary/(?P<download_type>\w+)/(?P<state_name>\w+)/(?P<registration_date>.+)$', views.registrationauthority.DataDictionaryDownloadOptionsView.as_view(), name='registrationauthority_data_dictionary_download_options'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/members', views.registrationauthority.MembersRegistrationAuthority.as_view(), name='registrationauthority_members'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/edit', views.registrationauthority.EditRegistrationAuthority.as_view(), name='registrationauthority_edit'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/states', views.registrationauthority.EditRegistrationAuthorityStates.as_view(), name='registrationauthority_edit_states'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/rules', views.registrationauthority.RAValidationRuleEditView.as_view(), name='registrationauthority_rules'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/add_user/?$', views.registrationauthority.AddUser.as_view(), name='registrationauthority_add_user'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/change_roles/(?P<user_pk>\d+)?/?$', views.registrationauthority.ChangeUserRoles.as_view(), name='registrationauthority_change_user_roles'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/remove/(?P<user_pk>\d+)/?$', views.registrationauthority.RemoveUser.as_view(), name='registrationauthority_member_remove'),
    path(r'^registrationauthority/(?P<iid>\d+)(?:/(?P<name_slug>.+))?/', views.registrationauthority.RegistrationAuthorityView.as_view(), name='registrationAuthority'),

    path(r'^organization/(?P<iid>\d+)?(?:/(?P<name_slug>.+))?/?$', views.registrationauthority.organization, name='organization'),
    path(r'^organizations/?$', views.registrationauthority.all_organizations, name='all_organizations'),
    path(r'^registrationauthorities/?$', views.registrationauthority.all_registration_authorities, name='all_registration_authorities'),

    path(r'^extensions/?$', views.extensions, name='extensions'),

    path(r'^notifyredirect/(?P<content_type>\d+)/(?P<object_id>\d+)/', views.notification_redirect, name="notify_redirect"),

    path(r'^about/aristotle/?$', TemplateView.as_view(template_name='aristotle_mdr/static/aristotle_mdr.html'), name="aboutMain"),
    path(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),

    path(r'^accessibility/?$', TemplateView.as_view(template_name='aristotle_mdr/static/accessibility.html'), name="accessibility"),

    path(r'user/(?P<uid>\d+)/profilePicture', views.user_pages.profile_picture, name="profile_picture"),
    path(r'user/(?P<uid>\d+)/profilePicture.svg', views.user_pages.profile_picture, name="dynamic_profile_picture"),

    path(r'share/(?P<share>[\w-]+)$', views.user_pages.SharedSandboxView.as_view(), name='sharedSandbox'),
    path(r'share/(?P<share>[\w-]+)/(?P<iid>\d+)', views.user_pages.SharedItemView.as_view(), name='sharedSandboxItem'),

    path(r'version/(?P<verid>\d+)', views.versions.ConceptVersionView.as_view(), name='item_version'),

    path(
        r'^search/?$',
        search_view_factory(
            view_class=PermissionSearchView,
            template='search/search.html',
            searchqueryset=None,
            form_class=forms.search.PermissionSearchForm
        ),
        name='search'
    ),
]
