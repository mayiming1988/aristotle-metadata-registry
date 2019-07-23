from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.slots import models as slot_models
from aristotle_mdr.contrib.links import models as link_models
from aristotle_mdr.contrib.aristotle_backwards import models as aristotle_backwards_models
from aristotle_mdr.contrib.stewards import models as aristotle_steward_models
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField, AristotleConceptFilterConnectionField
from aristotle_mdr_graphql.utils import type_from_model, type_from_concept_model, inline_type_from_model
from aristotle_mdr_graphql import resolvers


# ReviewRequestNode = type_from_model(mdr_models.ReviewRequest)
ConceptNode = type_from_concept_model(mdr_models._concept)
ObjectClassNode = type_from_concept_model(mdr_models.ObjectClass)
PropertyNode = type_from_concept_model(mdr_models.Property)
# MeasureNode = type_from_concept_model(mdr_models.Measure)
UnitOfMeasureNode = type_from_concept_model(mdr_models.UnitOfMeasure)
DataTypeNode = type_from_concept_model(mdr_models.DataType)
ConceptualDomainNode = type_from_concept_model(mdr_models.ConceptualDomain)
# ValueMeaningNode = inline_type_from_model(mdr_models.ValueMeaning)
PermissibleValueNode = inline_type_from_model(mdr_models.PermissibleValue)
SupplementaryValueNode = inline_type_from_model(mdr_models.SupplementaryValue)
WorkgroupNode = type_from_model(mdr_models.Workgroup)
LinkNode = type_from_model(link_models.Link)
LinkEndNode = type_from_model(link_models.LinkEnd)
relationNode = type_from_model(link_models.Relation)
relationRoleNode = type_from_model(link_models.RelationRole)
OrganizationNode = type_from_model(mdr_models.Organization)
recordRelationNode = type_from_model(mdr_models.RecordRelation)
OrganizationRecordNode = type_from_model(mdr_models.OrganizationRecord)
StewardOrganisationNode = type_from_model(mdr_models.StewardOrganisation)
DataElementConceptNode = type_from_concept_model(mdr_models.DataElementConcept)
dedinputs = inline_type_from_model(mdr_models.DedInputsThrough)
dedderives = inline_type_from_model(mdr_models.DedDerivesThrough)
DataElementDerivationNode = type_from_concept_model(mdr_models.DataElementDerivation)
SlotNode = inline_type_from_model(slot_models.Slot)
DataElementNode = type_from_concept_model(
    mdr_models.DataElement,
    extra_filter_fields=[
        'dataElementConcept',
        'valueDomain',
        'dataElementConcept__objectClass'
    ],
)
ValueDomainNode = type_from_concept_model(mdr_models.ValueDomain, resolver=resolvers.ValueDomainResolver())
ClassificationSchemeNode = type_from_concept_model(aristotle_backwards_models.ClassificationScheme)
CollectionNode = type_from_model(aristotle_steward_models.Collection)
RepresentationClassNode = type_from_model(aristotle_backwards_models.RepresentationClass)


class RegistrationAuthorityNode(DjangoObjectType):
    # At the moment, querying backward for a status from a registration authority has
    # permissions issues, and querying problems.
    # Lets come back to this one
    class Meta:
        model = mdr_models.RegistrationAuthority
        interfaces = (relay.Node, )
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
    # relation_roles = AristotleFilterConnectionField(relationRoleNode)
    # organizations = AristotleFilterConnectionField(OrganizationNode)
    registration_authorities = AristotleFilterConnectionField(RegistrationAuthorityNode)
    # discussion_posts = AristotleFilterConnectionField(DiscussionPostNode)
    # discussion_comments = AristotleFilterConnectionField(DiscussionCommentNode)
    # review_requests = AristotleFilterConnectionField(ReviewRequestNode)
    object_classes = AristotleConceptFilterConnectionField(ObjectClassNode)
    properties = AristotleConceptFilterConnectionField(PropertyNode)
    # measures = AristotleConceptFilterConnectionField(MeasureNode)
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

