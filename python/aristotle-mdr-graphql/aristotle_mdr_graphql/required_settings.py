GRAPHENE_DEBUG = False

GRAPHENE: dict = {
    'SCHEMA': 'aristotle_mdr_graphql.schema.schema',
}

if GRAPHENE_DEBUG:
    GRAPHENE['MIDDLEWARE'] = ['graphene_django.debug.DjangoDebugMiddleware']
