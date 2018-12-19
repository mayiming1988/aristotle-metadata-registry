from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'reviews/$', views.reviews.IssueCreateView.as_view(), name='review_create'),
    # url(r'reviews/(?P<pk>\d+)/$', views.reviews.IssueView.as_view(), name='reviews'),
    url(r'reviews/(?P<pk>\d+)/updatecomment/$', views.ReviewUpdateAndCommentView.as_view(), name='update_and_comment'),
    url(r'reviews/comments/$', views.ReviewCommentCreateView.as_view(), name='comment'),
    url(r'reviews/comments/(?P<pk>\d+)/$', views.ReviewCommentRetrieveView.as_view(), name='comment_get'),
]
