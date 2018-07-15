from datetime import timedelta

from django.utils import timezone

from germanium.annotations import data_provider
from germanium.test_cases.default import GermaniumTestCase
from germanium.tools import assert_equal, assert_true, assert_false

from freezegun import freeze_time

from verification_token.models import VerificationToken

from .base import BaseTestCaseMixin


__all__ = (
    'TokenTestCase',
)


class TokenTestCase(BaseTestCaseMixin, GermaniumTestCase):

    @data_provider('create_user')
    def test_verification_token_should_be_created_and_old_one_should_be_deactivated(self, user):
        token1 = VerificationToken.objects.deactivate_and_create(user)
        assert_true(token1.is_valid)
        assert_true(token1.is_active)
        token2 = VerificationToken.objects.deactivate_and_create(user)
        assert_true(token2.is_valid)
        assert_true(token2.is_active)
        token1.refresh_from_db()
        assert_false(token1.is_valid)
        assert_false(token1.is_active)

    @data_provider('create_user')
    def test_verification_token_with_different_slug_should_not_be_deactivated(self, user):
        token1 = VerificationToken.objects.deactivate_and_create(user, slug='a')
        assert_true(token1.is_valid)
        assert_true(token1.is_active)
        token2 = VerificationToken.objects.deactivate_and_create(user, slug='b')
        assert_true(token2.is_valid)
        assert_true(token2.is_active)
        token1.refresh_from_db()
        assert_true(token1.is_valid)
        assert_true(token1.is_active)

    @data_provider('create_user')
    def test_valid_verification_token_with_same_slug_should_exists(self, user):
        token = VerificationToken.objects.deactivate_and_create(user, slug='a')
        assert_true(VerificationToken.objects.exists_valid(user, slug='a', verification_key=token.key))
        assert_false(VerificationToken.objects.exists_valid(user, slug='b', verification_key=token.key))
        assert_false(VerificationToken.objects.exists_valid(user, slug='a', verification_key='invalid key'))

    @data_provider('create_user')
    def test_verification_should_be_invalid_after_expiration(self, user):
        token = VerificationToken.objects.deactivate_and_create(user, expiration_in_minutes=10)
        with freeze_time(timezone.now() + timedelta(minutes=10), tick=True):
            assert_false(token.is_valid)
            assert_true(token.is_active)
