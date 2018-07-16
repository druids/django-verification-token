import string

from django.conf import settings as django_settings


DEFAULTS = {
    'MAX_RANDOM_KEY_ITERATIONS': 100,  # Maximum iterations for random key generator
    'DEFAULT_KEY_LENGTH': 20,  # Default token key length
    'DEFAULT_KEY_CHARS': string.ascii_uppercase + string.digits,  # Allowed token key characters
    'DEFAULT_KEY_GENERATOR': 'verification_token.generators.random_string_generator',  # Token key generator
    'DEFAULT_EXPIRATION': 24 * 60,  # Default token expiration in minutes
}


class Settings:

    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError('Invalid VERIFICATION_TOKEN setting: "{}"'.format(attr))

        default = DEFAULTS[attr]
        return getattr(
            django_settings, 'VERIFICATION_TOKEN_{}'.format(attr), default(self) if callable(default) else default
        )


settings = Settings()
