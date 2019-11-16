import graphene
from graphene_django.types import DjangoObjectType
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.slots import models as slot_models
from aristotle_mdr.contrib.links import models as link_models
from aristotle_mdr.contrib.aristotle_backwards import models as aristotle_backwards_models
from aristotle_mdr.contrib.stewards import models as aristotle_steward_models
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField, AristotleConceptFilterConnectionField
from aristotle_mdr_graphql.utils import get_dynamic_type_node_from_model, get_dynamic_type_node_from_concept_model
from aristotle_mdr_graphql import resolvers
from aristotle_mdr_graphql.aristotle_filterset_classes import CollectionFilterSet, SupersedeRelationshipFilterSet
from aristotle_mdr_graphql.types import AristotleConceptObjectType

ConceptNode = get_dynamic_type_node_from_concept_model(model=mdr_models._concept)
ObjectClassNode = get_dynamic_type_node_from_concept_model(model=mdr_models.ObjectClass)
PropertyNode = get_dynamic_type_node_from_concept_model(model=mdr_models.Property)
UnitOfMeasureNode = get_dynamic_type_node_from_concept_model(model=mdr_models.UnitOfMeasure)
DataTypeNode = get_dynamic_type_node_from_concept_model(model=mdr_models.DataType)
ConceptualDomainNode = get_dynamic_type_node_from_model(model=mdr_models.ConceptualDomain)
PermissibleValueNode = get_dynamic_type_node_from_model(
    model=mdr_models.PermissibleValue,
    interfaces=[],  # We are overriding the default interface.
    object_type=DjangoObjectType,  # We are also overriding the Object Type.
)
SupplementaryValueNode = get_dynamic_type_node_from_model(
    model=mdr_models.SupplementaryValue,
    interfaces=[],  # We are overriding the default interface.
    object_type=DjangoObjectType,  # We are also overriding the Object Type.
)
WorkgroupNode = get_dynamic_type_node_from_model(model=mdr_models.Workgroup)
LinkNode = get_dynamic_type_node_from_model(model=link_models.Link, )
LinkEndNode = get_dynamic_type_node_from_model(model=link_models.LinkEnd, )
relationNode = get_dynamic_type_node_from_model(model=link_models.Relation, )
relationRoleNode = get_dynamic_type_node_from_model(model=link_models.RelationRole, )
OrganizationNode = get_dynamic_type_node_from_model(model=mdr_models.Organization, )
recordRelationNode = get_dynamic_type_node_from_model(model=mdr_models.RecordRelation, )
OrganizationRecordNode = get_dynamic_type_node_from_model(model=mdr_models.OrganizationRecord, )
StewardOrganisationNode = get_dynamic_type_node_from_model(model=mdr_models.StewardOrganisation, )
DataElementConceptNode = get_dynamic_type_node_from_concept_model(model=mdr_models.DataElementConcept)
dedinputs = get_dynamic_type_node_from_model(
    model=mdr_models.DedInputsThrough,
    interfaces=[],  # We are overriding the default interface.
    object_type=DjangoObjectType,  # We are also overriding the Object Type.
)
dedderives = get_dynamic_type_node_from_model(
    model=mdr_models.DedDerivesThrough,
    interfaces=[],  # We are overriding the default interface.
    object_type=DjangoObjectType,  # We are also overriding the Object Type.
)
DataElementDerivationNode = get_dynamic_type_node_from_concept_model(model=mdr_models.DataElementDerivation)
SlotNode = get_dynamic_type_node_from_model(
    model=slot_models.Slot,
    interfaces=[],  # We are overriding the default interface.
    object_type=DjangoObjectType,  # We are also overriding the Object Type.
)
DataElementNode = get_dynamic_type_node_from_model(
    model=mdr_models.DataElement,
    filter_fields=[
        'dataElementConcept',
        'valueDomain',
        'dataElementConcept__objectClass'
    ],
    object_type=AristotleConceptObjectType,
)
ValueDomainNode = get_dynamic_type_node_from_concept_model(
    model=mdr_models.ValueDomain,
    default_resolver=resolvers.ValueDomainResolver(),
)
ClassificationSchemeNode = get_dynamic_type_node_from_concept_model(
    model=aristotle_backwards_models.ClassificationScheme)
CollectionNode = get_dynamic_type_node_from_model(model=aristotle_steward_models.Collection,
                                                  filterset_class=CollectionFilterSet)
RepresentationClassNode = get_dynamic_type_node_from_model(model=aristotle_backwards_models.RepresentationClass)


class RegistrationAuthorityNode(DjangoObjectType):
    # At the moment, querying backward for a status from a registration authority has
    # permissions issues, and querying problems.
    # Lets come back to this one
    class Meta:
        model = mdr_models.RegistrationAuthority
        interfaces = (graphene.relay.Node,)
        filter_fields = ['name']
        default_resolver = resolvers.RegistrationAuthorityResolver()
        exclude_fields = ['status_set']


class ValueMeaningNode(DjangoObjectType):
    class Meta:
        model = mdr_models.ValueMeaning


class Query:
    metadata = AristotleConceptFilterConnectionField(
        ConceptNode,
        description="Retrieve a collection of untyped metadata",
    )
    workgroups = AristotleFilterConnectionField(WorkgroupNode)
    links = AristotleFilterConnectionField(LinkNode)
    link_ends = AristotleFilterConnectionField(LinkEndNode)
    relations = AristotleFilterConnectionField(relationNode)
    registration_authorities = AristotleFilterConnectionField(RegistrationAuthorityNode)
    object_classes = AristotleConceptFilterConnectionField(ObjectClassNode)
    properties = AristotleConceptFilterConnectionField(PropertyNode)
    unit_of_measures = AristotleConceptFilterConnectionField(UnitOfMeasureNode)
    data_types = AristotleConceptFilterConnectionField(DataTypeNode)
    conceptual_domains = AristotleConceptFilterConnectionField(ConceptualDomainNode)
    value_domains = AristotleConceptFilterConnectionField(ValueDomainNode)
    data_element_concepts = AristotleConceptFilterConnectionField(DataElementConceptNode)
    data_elements = AristotleConceptFilterConnectionField(DataElementNode)
    data_element_derivations = AristotleConceptFilterConnectionField(DataElementDerivationNode)
    classification_schemes = AristotleConceptFilterConnectionField(ClassificationSchemeNode)
    collections = AristotleFilterConnectionField(CollectionNode)
    stewards = AristotleFilterConnectionField(StewardOrganisationNode)
    organisation_record = AristotleFilterConnectionField(OrganizationRecordNode)
