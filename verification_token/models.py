import string

from datetime import timedelta

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.crypto import get_random_string


class VerificationTokenManager(models.Manager):

    def deactivate(self, obj, slug=None, key=None):
        self.filter_active_tokens(obj, slug, key).update(is_active=False)

    def deactivate_and_create(self, obj, slug=None, deactivate_old_tokens=True, expiration_in_minutes=24 * 60):
        if deactivate_old_tokens:
            self.deactivate(obj, slug)
        return self.create(
            content_type=ContentType.objects.get_for_model(obj.__class__),
            object_id=obj.pk,
            slug=slug,
            expiration_in_minutes=expiration_in_minutes
        )

    def exists_valid(self, obj, verification_key, slug=None):
        for token in self.filter_active_tokens(obj, slug):
            if token.check_key(verification_key):
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

    objects = VerificationTokenManager()

    def generate_key(self, length=20, allowed_chars=string.ascii_uppercase + string.digits):
        return get_random_string(length, allowed_chars)

    @property
    def is_valid(self):
        return (
            self.is_active and self.key and self.expiration_in_minutes and
            timezone.now() <= self.created_at + timedelta(minutes=self.expiration_in_minutes)
        )

    def check_key(self, verification_key):
        """
        Returns True iff verification key is correct and not expired
        """
        return self.is_valid and self.key == verification_key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ('-created_at',)
