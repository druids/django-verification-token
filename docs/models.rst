.. _models:

Models
======

.. class:: auth_token.models.VerificationToken

  Verification token can be used for password reset or other authorization methods via e-mail, SMS or other media.

  .. attribute:: created_at

    ``DateTimeField``, contains date and time of token creation.

  .. attribute:: content_type

    Content type of the verified object.

  .. attribute:: object_id

    Identifier of the verified object.

  .. attribute:: content_object

    Verified object (``GenericForeignKey``)

  .. attribute:: key

    Verification token value.

  .. attribute:: expiration_in_minutes

    Token expiration in minutes.

  .. attribute:: slug

    Slug that can be used for token purposes definition.

  .. attribute:: is_active

    ``BooleanField`` contains if token is active.

  .. method:: generate_key(generator=None, *args, **kwargs)

    Class method for unique token key generation. You can send generator and its args and kwargs. If generator is not set default generator is used (``VERIFICATION_TOKEN_DEFAULT_KEY_GENERATOR``).

  .. method:: is_valid()

    Method which checks whether token is active and is not expired.

Managers
========

.. class:: auth_token.models.VerificationTokenManager

  Manager of ``auth_token.models.VerificationToken`` model, provides methods for token creation, validation and deactivation.

  .. method:: deactivate(obj, slug=None, key=None)

    Deactivates all tokens related to model. If slug or key is send only tokens with the slug and key are deactivated.

  .. method:: deactivate_and_create(obj, obj, slug=None, deactivate_old_tokens=True, expiration_in_minutes=None, key_generator_kwargs=None)

    Method deactivates old tokens and generate new one. Deactivation can be disabled via parameter ``deactivate_old_tokens``. Parameter ``key_generator_kwargs`` can be used for changing key generator kwargs (kwargs of class method ``auth_token.models.VerificationToken.generate_key``).

  .. method:: exists_valid(obj, slug=None, key=None)

    Checks if exists valid token related to the object with the ``slug`` and ``key``. Parameters ``slug`` and ``key`` can be empty to deactivate all object tokens.

  .. method:: filter_active_tokens(obj, slug=None, key=None)

    Method for getting all active tokens related to the object, slug and key.
