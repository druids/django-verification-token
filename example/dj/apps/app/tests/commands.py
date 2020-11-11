from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

from freezegun import freeze_time
from germanium.annotations import data_provider
from germanium.test_cases.default import GermaniumTestCase
from germanium.tools import assert_equal
from germanium.tools.models import assert_qs_contains, assert_qs_not_contains
from verification_token.models import VerificationToken

from .base import BaseTestCaseMixin


__all__ = (
   'CleanVerificationTokensCommandTestCase',
)


class CleanVerificationTokensCommandTestCase(BaseTestCaseMixin, GermaniumTestCase):

    @freeze_time(timezone.now())
    @data_provider('create_user')
    def test_clean_verification_tokens_removes_only_non_active_tokens(self, user):
        active_tokens_without_expirations = [VerificationToken.objects.deactivate_and_create(
            obj=user, deactivate_old_tokens=False, expiration_in_minutes=None) for _ in range(10)]
        active_tokens_with_expirations = [VerificationToken.objects.deactivate_and_create(
            obj=user, deactivate_old_tokens=False, expiration_in_minutes=5) for _ in range(10)]
        expired_tokens = [VerificationToken.objects.deactivate_and_create(
            obj=user, deactivate_old_tokens=False, expiration_in_minutes=1) for _ in range(10)]
        deactivated_tokens = [VerificationToken.objects.deactivate_and_create(
            obj=user, deactivate_old_tokens=False, expiration_in_minutes=None) for _ in range(10)]
        VerificationToken.objects.filter(pk__in=[token.pk for token in deactivated_tokens]).update(is_active=False)
        expired_and_deactivated_tokens = [VerificationToken.objects.deactivate_and_create(
            obj=user, deactivate_old_tokens=False, expiration_in_minutes=1) for _ in range(10)]
        VerificationToken.objects.filter(pk__in=[token.pk for token in expired_and_deactivated_tokens]).update(
            is_active=False)

        with freeze_time(timezone.now()+timedelta(minutes=2)):
            call_command('clean_verification_tokens', stdout=StringIO(), stderr=StringIO())

            all_tokens_qs = VerificationToken.objects.all()
            assert_qs_contains(all_tokens_qs, active_tokens_without_expirations)
            assert_qs_contains(all_tokens_qs, active_tokens_with_expirations)
            assert_qs_not_contains(all_tokens_qs, expired_tokens)
            assert_qs_not_contains(all_tokens_qs, deactivated_tokens)
            assert_qs_not_contains(all_tokens_qs, expired_and_deactivated_tokens)
