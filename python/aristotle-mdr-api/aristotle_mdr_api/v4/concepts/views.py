from rest_framework import generics
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit
from aristotle_mdr_api.v4.concepts import serializers
from aristotle_mdr.models import _concept


class ConceptView(generics.RetrieveAPIView):
    permission_classes=(AuthCanViewEdit,)
    permission_key='metadata'
    serializer_class=serializers.ConceptSerializer
    queryset=_concept.objects.all()
