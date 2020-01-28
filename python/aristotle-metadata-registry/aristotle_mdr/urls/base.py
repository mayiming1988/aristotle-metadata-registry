
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

from aristotle_mdr.views.user_pages import FriendlyLoginView, FriendlyLogoutView
from aristotle_mdr.contrib.user_management.views import AristotlePasswordResetView

admin.autodiscover()

urlpatterns = [
    path('login', FriendlyLoginView.as_view(), name='friendly_login'),
    path('logout/', FriendlyLogoutView.as_view(), name='logout'),
    path('django/admin/doc/', include('django.contrib.admindocs.urls')),
    path('django/admin/', admin.site.urls),
    path('ckeditor/', include('aristotle_mdr.urls.ckeditor_uploader')),
    re_path('account/sessions/?$', RedirectView.as_view(url=reverse_lazy("aristotle:userProfile"), permanent=False)),
    path('account/password/reset/', AristotlePasswordResetView.as_view()),
    path('account/password/reset_done/', AristotlePasswordResetView.as_view()),
    path('user/password/reset/', AristotlePasswordResetView.as_view(),
         {'post_reset_redirect': '/user/password/reset/done/'},
         name="password_reset"
         ),
    path('user/password/reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name="password_reset_done"
         ),
    re_path(
        r'user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path('user/password/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('account/password/', RedirectView.as_view(url='account/home/', permanent=True)),
    path('account/password/change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('account/password/change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('', include('user_sessions.urls', 'user_sessions')),
]
