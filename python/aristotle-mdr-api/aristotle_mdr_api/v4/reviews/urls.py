from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'(?P<pk>\d+)/promote-item/$', views.PromoteImpactedItemToReviewItemsView.as_view(), name='promote_item'),
    url(r'(?P<pk>\d+)/updatecomment/$', views.ReviewUpdateAndCommentView.as_view(), name='update_and_comment'),
    url(r'comments/$', views.ReviewCommentCreateView.as_view(), name='comment'),
    url(r'comments/(?P<pk>\d+)/$', views.ReviewCommentRetrieveView.as_view(), name='comment_get'),
]
