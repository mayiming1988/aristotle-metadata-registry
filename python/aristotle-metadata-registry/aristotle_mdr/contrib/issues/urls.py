from django.urls import path
from aristotle_mdr.contrib.issues import views

urlpatterns = [
    path('item/<int:iid>/issues/', views.IssueList.as_view(), name='item_issues'),
    path('item/<int:iid>/issue/<int:pk>/', views.IssueDisplay.as_view(), name='issue'),
    path('account/admin/issues/labels/', views.admin.IssueLabelList.as_view(), name='admin_issue_label_list'),
    path('account/admin/issues/label/create/', views.admin.IssueLabelCreate.as_view(), name='admin_labels_create'),
    path('account/admin/issues/label/update/<int:pk>/', views.admin.IssueLabelUpdate.as_view(), name='admin_labels_update'),
    path('account/admin/issues/label/delete/<int:pk>/', views.admin.IssueLabelDelete.as_view(), name='admin_labels_delete'),
]
