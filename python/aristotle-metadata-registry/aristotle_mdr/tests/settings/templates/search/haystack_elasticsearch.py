# TODO: this needs to be fixed
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'document',
#     },
# }
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': 'http://elasticsearch:9200',
        'INDEX_NAME': 'test_index',
        'INCLUDE_SPELLING': True,
        'KWARGS': {
            'http_auth': 'elastic:changeme'
                }
            }
        }

