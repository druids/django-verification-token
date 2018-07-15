.. _installation:

Installation
============

Using PIP
---------

You can install django-verification-token via pip:

.. code-block:: console

    $ pip install django-verification-token


Configuration
=============

After installation you must go through these steps:

Required Settings
-----------------

The following variables have to be added to or edited in the project's ``settings.py``:

For using the library you just add ``verification_token`` to ``INSTALLED_APPS`` variable::

    INSTALLED_APPS = (
        ...
        'verification_token',
        ...
    )
