The Aristotle REST API
======================

Description
-----------

The Aristotle REST API's are (avaliable at /api/) provide access to content within the system in a machine readable form

The api is versioned and deprecated slowly so that existing applications have time to transition. Currently v3 and v4 are avaliable.

Swagger documentation is automatically generated for each api. This describes the endpoints along with expected data and is avaliable at /api/v3 and /api/v4

Authentication
--------------

To access private content through the api you need to either be logged in to the site or provide an access token.

Access tokens can be created from the token management page and must be assigned explict permissions which determined the endpoints each token is able to access.

To use the token it must be provided in the Authenticate http header in the form Token: mytoken. For example if your token is ``Ykc7ClFLUiQKKG8`` the Authenticate header should be ``Token: Ykc7ClFLUiQKKG8``
