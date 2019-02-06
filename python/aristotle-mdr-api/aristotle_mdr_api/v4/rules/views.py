from aristotle_mdr_api.v4.rules import serializers
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView


class CreateRARules(CreateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class = serializers.RARuleSerializer


class RetrieveUpdateRARules(RetrieveUpdateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class = serializers.RARuleSerializer


class CreateRegistryRules(CreateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class = serializers.RegistryRuleSerializer


class RetrieveUpdateRegistryRules(RetrieveUpdateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class = serializers.RegistryRuleSerializer
