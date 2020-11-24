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

  .. attribute:: expires_at

    ``DateTimeField``, contains date and time of token expiration or None (for a token that never expires).

  .. attribute:: slug

    Slug that can be used for token purposes definition.

  .. attribute:: is_active

    ``BooleanField`` contains if token is active.

  .. attribute:: extra_data

    ``TextField``, contains arbitrary data related to the token in JSON format. Use methods ``get_extra_data()`` and ``set_extra_data()`` to access it.

  .. method:: generate_key(generator=None, *args, **kwargs)

    Class method for unique token key generation. You can send generator and its args and kwargs. If generator is not set default generator is used (``VERIFICATION_TOKEN_DEFAULT_KEY_GENERATOR``).

  .. method:: is_valid()

    Method which checks whether token is active and is not expired.

  .. method:: set_extra_data(extra_data)

    Converts `extra_data` (JSON serializable object) to JSON and sets it to the token.

  .. method:: get_extra_data()

    Returns deserialized `extra_data`.

Managers
========

.. class:: auth_token.models.VerificationTokenManager

  Manager of ``auth_token.models.VerificationToken`` model, provides methods for token creation, validation and deactivation.

  .. method:: deactivate(obj, slug=None, key=None)

    Deactivates all tokens related to model. If slug or key is send only tokens with the slug and key are deactivated.

  .. method:: deactivate_and_create(obj, obj, slug=None, extra_data=None, deactivate_old_tokens=True, expiration_in_minutes=None, key_generator_kwargs=None)

    Method deactivates old tokens and generate new one. Deactivation can be disabled via parameter ``deactivate_old_tokens``. Parameter ``key_generator_kwargs`` can be used for changing key generator kwargs (kwargs of class method ``auth_token.models.VerificationToken.generate_key``).

  .. method:: exists_valid(obj, slug=None, key=None)

    Checks if exists valid token related to the object with the ``slug`` and ``key``. Parameters ``slug`` and ``key`` can be empty to deactivate all object tokens.

  .. method:: filter_active_tokens(obj, slug=None, key=None)

    Method for getting all active tokens related to the object, slug and key.
