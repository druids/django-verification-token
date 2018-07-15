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
