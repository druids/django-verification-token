from datetime import timedelta

from django.db.utils import IntegrityError
from django.utils import timezone
from django.test import override_settings

from germanium.annotations import data_provider
from germanium.test_cases.default import GermaniumTestCase
from germanium.tools import assert_equal, assert_true, assert_false, assert_raises

from freezegun import freeze_time

from verification_token.models import VerificationToken

from .base import BaseTestCaseMixin


__all__ = (
    'TokenTestCase',
)


class Counter:

    def __init__(self):
        self.iterations = 0

    def add(self):
        self.iterations += 1


def test_generator():
    return 'test'


def generator_with_counter(counter):
    counter.add()
    return 'not_unique'


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
        assert_true(VerificationToken.objects.exists_valid(user, slug='a', key=token.key))
        assert_false(VerificationToken.objects.exists_valid(user, slug='b', key=token.key))
        assert_false(VerificationToken.objects.exists_valid(user, slug='a', key='invalid key'))

    @data_provider('create_user')
    def test_verification_token_should_be_invalid_after_expiration(self, user):
        token = VerificationToken.objects.deactivate_and_create(user, expiration_in_minutes=10)
        with freeze_time(timezone.now() + timedelta(minutes=10), tick=True):
            assert_false(token.is_valid)
            assert_true(token.is_active)

    @data_provider('create_user')
    @override_settings(VERIFICATION_TOKEN_DEFAULT_EXPIRATION=10)
    def test_verification_token_expiration_should_be_set_via_settings(self, user):
        token = VerificationToken.objects.deactivate_and_create(user)
        with freeze_time(timezone.now() + timedelta(minutes=10), tick=True):
            assert_false(token.is_valid)
            assert_true(token.is_active)

    @data_provider('create_user')
    def test_key_generator_values_should_be_able_to_change(self, user):
        token = VerificationToken.objects.deactivate_and_create(
            user, key_generator_kwargs={'length': 100, 'allowed_chars': 'abc'
        })
        assert_equal(len(token.key), 100)
        assert_false(set(token.key) - set('abc'))

    @data_provider('create_user')
    @override_settings(VERIFICATION_TOKEN_DEFAULT_KEY_LENGTH=100, VERIFICATION_TOKEN_DEFAULT_KEY_CHARS='abc')
    def test_key_generator_values_should_be_able_to_change_via_settings(self, user):
        token = VerificationToken.objects.deactivate_and_create(user)
        assert_equal(len(token.key), 100)
        assert_false(set(token.key) - set('abc'))

    @data_provider('create_user')
    def test_key_generator_should_be_able_to_change(self, user):
        token = VerificationToken.objects.deactivate_and_create(user, key_generator_kwargs={
            'generator': test_generator
        })
        assert_equal(token.key, 'test')

    @data_provider('create_user')
    @override_settings(VERIFICATION_TOKEN_DEFAULT_KEY_GENERATOR=test_generator)
    def test_key_generator_should_be_able_to_change_via_settings(self, user):
        token = VerificationToken.objects.deactivate_and_create(user)
        assert_equal(token.key, 'test')

    @data_provider('create_user')
    @override_settings(VERIFICATION_TOKEN_MAX_RANDOM_KEY_ITERATIONS=12)
    def test_key_generator_iterations_should_be_according_to_settings(self, user):
        counter = Counter()
        token = VerificationToken.objects.deactivate_and_create(user, key_generator_kwargs={
            'generator': generator_with_counter, 'counter': counter
        })
        assert_equal(token.key, 'not_unique')
        assert_equal(counter.iterations, 1)

        counter = Counter()
        with assert_raises(IntegrityError):
            VerificationToken.objects.deactivate_and_create(user, key_generator_kwargs={
                'generator': generator_with_counter, 'counter': counter
            })
        assert_equal(counter.iterations, 12)

    @data_provider('create_user')
    def test_verification_token_should_store_extra_data(self, user):
        EXTRA_DATA_1 = {'a': 123}
        EXTRA_DATA_2 = {'b': 456}

        token = VerificationToken.objects.deactivate_and_create(user, extra_data=EXTRA_DATA_1)
        token.refresh_from_db()
        assert_equal(token.get_extra_data(), EXTRA_DATA_1)

        token.set_extra_data(EXTRA_DATA_2)
        token.save()
        token.refresh_from_db()
        assert_equal(token.get_extra_data(), EXTRA_DATA_2)
