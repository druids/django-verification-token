from django.utils.crypto import get_random_string

from .config import settings


def random_string_generator(length=None, allowed_chars=None):
    length = settings.DEFAULT_KEY_LENGTH if length is None else length
    allowed_chars = settings.DEFAULT_KEY_CHARS if allowed_chars is None else allowed_chars

    return get_random_string(length, allowed_chars)
