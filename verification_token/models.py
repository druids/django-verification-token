import json
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.module_loading import import_string

from .config import settings


class VerificationTokenManager(models.Manager):

    def deactivate(self, obj, slug=None, key=None):
        self.filter_active_tokens(obj, slug, key).update(is_active=False)

    def deactivate_and_create(self, obj, slug=None, extra_data=None, deactivate_old_tokens=True,
                              key_generator_kwargs=None, **kwargs):
        if deactivate_old_tokens:
            self.deactivate(obj, slug)

        return self._create(obj, slug=slug, extra_data=extra_data, key_generator_kwargs=key_generator_kwargs, **kwargs)

    def get_active_or_create(self, obj, slug=None, extra_data=None, key=None, key_generator_kwargs=None, **kwargs):
        token = self.filter_active_tokens(obj, slug, key).order_by('created_at').last()

        if token and token.is_valid:
            return token
        else:
            return self._create(obj, slug=slug, extra_data=extra_data, key_generator_kwargs=key_generator_kwargs,
                                **kwargs
            )

    def _create(self, obj, slug=None, extra_data=None, key_generator_kwargs=None, **kwargs):
        expiration_in_minutes = kwargs.pop('expiration_in_minutes', settings.DEFAULT_EXPIRATION)
        key_generator_kwargs = {} if key_generator_kwargs is None else key_generator_kwargs

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

    def filter_active_tokens(self, obj_or_class, slug=None, key=None):
        qs = self.filter(
            is_active=True,
            slug=slug,
            content_type=ContentType.objects.get_for_model(obj_or_class),
        )
        if isinstance(obj_or_class, models.Model):
            qs = qs.filter(object_id=obj_or_class.pk)
        return qs.filter(key=key) if key else qs


class VerificationToken(models.Model):
    """
    Specific verification tokens that can be send via e-mail to check user authorization (example password reset)
    """

    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.TextField(db_index=True)
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
            self.is_active and self.key and (self.expiration_in_minutes is None or timezone.now() <=
                                             self.created_at + timedelta(minutes=self.expiration_in_minutes))
        )

    def check_key(self, key):
        """
        Returns True if verification key is correct and not expired
        """
        return self.is_valid and self.key == key

    def set_extra_data(self, extra_data):
        self.extra_data = json.dumps(extra_data)

    def get_extra_data(self):
        return json.loads(self.extra_data) if self.extra_data is not None else None

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ('-created_at',)
