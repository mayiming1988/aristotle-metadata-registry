from graphene_django.types import DjangoObjectType
from aristotle_mdr_graphql.fields import AristotleConceptFilterConnectionField
from aristotle_dse import models as dse_models
from aristotle_mdr_graphql.utils import get_dynamic_type_node_from_concept_model
from aristotle_mdr_graphql import resolvers

# DataCatalogNode = get_dynamic_type_node_from_model(
#     model=dse_models.DataCatalog,
#     filterset_class=ConceptFilterSet,
#     object_type=AristotleConceptObjectType,
# )
DatasetNode = get_dynamic_type_node_from_concept_model(model=dse_models.Dataset)
DistributionNode = get_dynamic_type_node_from_concept_model(model=dse_models.Distribution)
# DistributionDataElementPathNode = get_dynamic_type_node_from_model(
#     model=dse_models.DistributionDataElementPath,
# )
DataSetSpecificationNode = get_dynamic_type_node_from_concept_model(
    model=dse_models.DataSetSpecification,
    default_resolver=resolvers.DataSetSpecificationResolver(),
    meta_kwargs={"exclude_fields": ['data_elements']},
)
# DSSDEInclusionNode = get_dynamic_type_node_from_model(model=dse_models.DSSDEInclusion)
# DSSClusterInclusionNode = get_dynamic_type_node_from_model(model=dse_models.DSSClusterInclusion)


class DSSDEInclusionNode(DjangoObjectType):
    class Meta:
        model = dse_models.DSSDEInclusion
        default_resolver = resolvers.DSSInclusionResolver()


class DSSClusterInclusionNode(DjangoObjectType):
    class Meta:
        model = dse_models.DSSClusterInclusion
        default_resolver = resolvers.DSSInclusionResolver()


class Query:

    # data_catalogs = AristotleConceptFilterConnectionField(DataCatalogNode)
    datasets = AristotleConceptFilterConnectionField(DatasetNode)
    # distributions = AristotleConceptFilterConnectionField(DistributionNode)
    dataset_specifications = AristotleConceptFilterConnectionField(DataSetSpecificationNode)
