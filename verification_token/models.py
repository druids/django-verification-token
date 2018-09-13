import json
import string

from datetime import timedelta

from django.db import models
from django.db.utils import IntegrityError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.module_loading import import_string

from .config import settings


class VerificationTokenManager(models.Manager):

    def deactivate(self, obj, slug=None, key=None):
        self.filter_active_tokens(obj, slug, key).update(is_active=False)

    def deactivate_and_create(self, obj, slug=None, extra_data=None, deactivate_old_tokens=True, expiration_in_minutes=None,
                              key_generator_kwargs=None):
        expiration_in_minutes = settings.DEFAULT_EXPIRATION if expiration_in_minutes is None else expiration_in_minutes

        key_generator_kwargs = {} if key_generator_kwargs is None else key_generator_kwargs
        if deactivate_old_tokens:
            self.deactivate(obj, slug)

        token = self.model(
            content_type=ContentType.objects.get_for_model(obj.__class__),
            object_id=obj.pk,
            slug=slug,
            expiration_in_minutes=expiration_in_minutes,
            key=self.model.generate_key(**key_generator_kwargs),
        )
        if extra_data:
            token.set_extra_data(extra_data)

        token.save()
        return token

    def exists_valid(self, obj, key, slug=None):
        for token in self.filter_active_tokens(obj, slug):
            if token.check_key(key):
                return True
        return False

    def filter_active_tokens(self, obj, slug=None, key=None):
        qs = self.filter(
            is_active=True,
            slug=slug,
            content_type=ContentType.objects.get_for_model(obj.__class__),
            object_id=obj.pk
        )
        return qs.filter(key=key) if key else qs


class VerificationToken(models.Model):
    """
    Specific verification tokens that can be send via e-mail to check user authorization (example password reset)
    """

    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.TextField()
    content_object = GenericForeignKey('content_type', 'object_id')
    key = models.CharField(null=False, blank=False, max_length=100, unique=True)
    expiration_in_minutes = models.PositiveIntegerField(null=True, blank=True, default=None)
    slug = models.SlugField(null=True, blank=True)
    is_active = models.BooleanField(null=False, blank=False, default=True)
    extra_data = models.TextField(null=True, blank=True)

    objects = VerificationTokenManager()

    @classmethod
    def generate_key(cls, generator=None, *args, **kwargs):
        """
        Generate random unique token key.
        """
        generator = settings.DEFAULT_KEY_GENERATOR if generator is None else generator
        generator_func = import_string(generator) if isinstance(generator, str) else generator

        key = generator_func(*args, **kwargs)
        try_generator_iterations = 1
        while cls.objects.filter(key=key).exists():
            if try_generator_iterations >= settings.MAX_RANDOM_KEY_ITERATIONS:
                raise IntegrityError('Could not produce unique key for verification token')
            try_generator_iterations += 1
            key = generator_func(*args, **kwargs)
        return key

    @property
    def is_valid(self):
        return (
            self.is_active and self.key and self.expiration_in_minutes and
            timezone.now() <= self.created_at + timedelta(minutes=self.expiration_in_minutes)
        )

    def check_key(self, key):
        """
        Returns True if verification key is correct and not expired
        """
        return self.is_valid and self.key == key

    def set_extra_data(self, extra_data):
        self.extra_data = json.dumps(extra_data)

    def get_extra_data(self):
        return json.loads(self.extra_data)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ('-created_at',)
