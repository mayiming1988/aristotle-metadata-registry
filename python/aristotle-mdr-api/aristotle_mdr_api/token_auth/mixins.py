from django.http import HttpResponse, Http404
from aristotle_mdr_api.token_auth.models import AristotleToken
from rest_framework.permissions import SAFE_METHODS


class TokenAuthMixin:
    """
    Mixin for using tokens outside of django rest framework
    Currently used in graphql views
    """

    header_prefix: str = 'Token: '
    permission_key: str = 'default'

    def dispatch(self, request, *args, **kwargs):
        if 'AUTHORIZATION' in request.META:
            auth_header = request.META['AUTHORIZATION']
            if auth_header.startswith(self.header_prefix):
                token = auth_header[len(self.header_prefix):]
                try:
                    token_obj = AristotleToken.objects.get(key=token)
                except AristotleToken.DoesNotExist:
                    return HttpResponse(content='Invalid authorization header', status=400)

                has_perms = self.check_token_permission(request, token_obj)
                if not has_perms:
                    return HttpResponse(content='Token does not have permission to perform this action', status=403)

                self.user = token_obj.user
            else:
                return HttpResponse(content='Invalid authorization header', status=400)
        else:
            return self.handle_non_token_request(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    def handle_non_token_request(self, request, *args, **kwargs):
        raise Http404

    def check_token_permission(self, request, token):
        permissions = token.permissions
        if self.permission_key in permissions:
            sub_perms = permissions[self.permission_key]
            # If read method and read perm
            if request.method in SAFE_METHODS and sub_perms['read']:
                return True
            # If write method and write perm
            if request.method not in SAFE_METHODS and sub_perms['write']:
                return True

        return False
