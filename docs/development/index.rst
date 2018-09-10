
Developing and contributing to the Aristotle Metadata Registry
==============================================================

Aristotle-MDR is a complex tool, so this is a guide on how you can easily
contribute to the development of Aristotle.

.. toctree::
   :maxdepth: 2

   environment.rst

.. note:: In this page, we assume your registry is at ``aristotle.example.com``. Update your URLs accordingly when running commands.

Creating a superuser
--------------------

``docker-compose exec web django-admin createsuperuser``

Quickly switching user roles   
----------------------------

Its often easy to interact with the registry as a super user, however often you will
want to test how users with different roles will interact with the site.

To make this easier, in development by default ``django-impersonate`` is installed.
Using this you can quickly switch users by going to the ``aristotle.example.com/alias/list``
page.

To stop acting as a different user go to ``aristotle.example.com/alias/stop``.
