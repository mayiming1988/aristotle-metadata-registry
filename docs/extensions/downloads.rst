Adding new download formats
===========================

While the Aristotle-MDR framework has a PDF download extension, it may be
desired to download metadata stored within a registry in a variety of download
formats. Rather than include these within the Aristotle-MDR core codebase,
additional download formats can be developed included via the download API.

Downloads architecture
---------------------------

There are two parts to the downloads module

* Django views will serve and it will start a job with Celery that will yield a download file asynchronously.
* Celery will have the tasks registered from the downloads class. Celery worker will add the file to a redis cache.

Creating a download module
---------------------------

A download module is a specialised class, that sub-classes ``aristotle_mdr.downloader.Downloader``
and provides an appropriate ``get_download_config`` and ``download`` or ``get_bulk_download_config`` and ``bulk_download`` methods.

A download module is just a Django app that includes a specific set
of files for generating downloads. The only files required in your app are:

* ``__init__.py`` - to declare the app as a python module
* ``downloader.py`` - where your download classes will be stored

Other modules can be written, for example a download module may define models for
recording a number of times an item is downloaded.

Writing a ``metadata_register``
-------------------------------
Your downloader class must contain a register of download types and the metadata concept
types which this module provides downloads for. This takes one of the following forms
which define which concepts can be downloaded as in the output format::

    class CSVExample(Downloader):
        download_type = "csv"
        metadata_register = {'aristotle_mdr': ['valuedomain']}

    class XLSExample(Downloader):
        download_type = "xls"
        metadata_register = {'aristotle_mdr': ['__all__']}

    class PDFExample(Downloader):
        download_type = "pdf"
        metadata_register = '__template__'

    class TXTExample(Downloader):
        download_type = "txt"
        metadata_register = '__all__'

Describing these options, these classes specifies the following downloads:

* ``csv`` provides downloads for Value Domains in the Aristotle-MDR module
* ``xls`` provides downloads for all metadata types in the Aristotle-MDR module
* ``pdf`` provides downloads for items in all modules, only if they have a download template
* ``txt`` provides downloads for all metadata types in all modules

Each download class must also define a class method with the following signature::

    def get_download_config(cls, request, iid):
        return properties, iid

This is a download config which creates the json serializable properties for the request.
This will ensure that the task can be passed on to Celery, which requires the objects to be json serializable.

The arguments are 

* ``request`` - the `request object <https://docs.djangoproject.com/en/stable/ref/request-response/>`_
  that was used to call the download view. The current user trying to download the
  item can be gotten by calling ``request.user``.

* ``iid`` - This is the id of the item that needs to be downloaded

The return arguments are:

* ``properties`` - This will save essential information like user email(can be used by celery to get user object) and title of the document(to be displayed to the user while the download is generated).
* ``iid`` - This would be same as the input argument in most cases. It is present to manipulate the iid if required.


Each download class must also define a static method with the following signature::

    @shared_task
    def download(properties, iid):

A shared task is a celery worker hook which will register this function as a celery task
This is called from Aristotle-MDR when it catches a download type that has been
registered for this module. The arguments are:

* ``properties`` - This will contain all the variables required by celery task to prepare the download.

* ``iid`` - the id of the item to be downloaded, to be retrieved from the database.

**Note:** If a download method is called the user has been verified to have
permissions to view the requested item only. Permissions for other items will
have to be checked within the download method.

The ``get_bulk_download_config`` and ``bulk_download`` method works in same fashion as ``get_download_config`` and ``download`` respectively.

For more information see the ``Downloader`` class below:

.. autoclass:: aristotle_mdr.downloader.Downloader
   :members:


How the ``download`` view works
-------------------------------

.. automodule:: aristotle_mdr.views.downloads
   :members: download
