The Aristotle GraphQL API
=========================

Description
-----------

The Aristotle GraphQL API provides read access to system data through the use of GraphQL queries.
See graphql.org for more information

You can test it out in GraphiQL by visiting ``/api/graphql``

Usage from external applications
--------------------------------

To query GraphQL from external applications you should use the ``/api/graphql/json`` endpoint. 
You can use a GET request with the query and optional JSON encoded variables parmaters for example:

/api/graphql/external?query={metadata{edges{node{uuid}}}}&variables=" optional JSON encoded variables "

Or you can make a POST request with either JSON or direct GraphQL. JSON must be submitted with the ``application/json`` content type and be in the following form with variables being optional.

::

    {
        "query": ...
        "variables": { ... }
    }

To submit a query directly you can use the ``application/graphql`` content type, although you will not be able to provide variables, making JSON the preferred method.

The response (from either a GET or POST request) will be JSON in the form ``{"data": { ... }}`` if the query was successful or ``{"errors": [ ... ]}`` if there was an error.

Authentication
--------------

By default the GraphQL endpoint will provide only public content. 
To access private content a token must be provided in the Authenticate header in the form ``Token: mytoken``. 
These tokens can be created from the token management page accessible from ``/api/``
