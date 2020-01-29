from django.conf.urls import url
from aristotle_mdr.contrib.issues import views

urlpatterns = [
    url(r'^item/(?P<iid>\d+)/issues/?$', views.IssueList.as_view(), name='item_issues'),
    url(r'^item/(?P<iid>\d+)/issue/(?P<pk>\d+)/?$', views.IssueDisplay.as_view(), name='issue'),
    url(r'^account/admin/issues/labels/?$', views.admin.IssueLabelList.as_view(), name='admin_issue_label_list'),
    url(r'^account/admin/issues/label/create/?$', views.admin.IssueLabelCreate.as_view(), name='admin_labels_create'),
    url(r'^account/admin/issues/label/update/(?P<pk>\d+)$', views.admin.IssueLabelUpdate.as_view(), name='admin_labels_update'),
    url(r'^account/admin/issues/label/delete/(?P<pk>\d+)$', views.admin.IssueLabelDelete.as_view(), name='admin_labels_delete'),
]
