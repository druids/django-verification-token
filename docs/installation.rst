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

Setup
-----

.. attribute:: VERIFICATION_TOKEN_MAX_RANDOM_KEY_ITERATIONS

  Verification token key is generated as random string. Because space of random strings is limited there can be collisions. Setting sets number of attempts to generate unique string. Default value is ``100``.

.. attribute:: VERIFICATION_TOKEN_DEFAULT_KEY_GENERATOR

  Default token generator function. You can use path to the function in string format or function itself. Default value is ``'verification_token.generators.random_string_generator'``.


.. attribute:: VERIFICATION_TOKEN_DEFAULT_KEY_LENGTH

  Verification token key length used by ``'verification_token.generators.random_string_generator'``. Maximal value is ``100``. Default value is ``20``.


.. attribute:: VERIFICATION_TOKEN_DEFAULT_KEY_CHARS

  Allowed characters used for token key generation with ``'verification_token.generators.random_string_generator'``. Default value is ``string.ascii_uppercase + string.digits``.


.. attribute:: VERIFICATION_TOKEN_DEFAULT_EXPIRATION

  Default token expiration time in minutes. Default value is ``24 * 60`` (one day).
