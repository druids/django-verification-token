from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.db.utils import IntegrityError
from django.test import override_settings
from django.utils import timezone

from freezegun import freeze_time
from germanium.annotations import data_provider
from germanium.test_cases.default import GermaniumTestCase
from germanium.tools import (assert_equal, assert_false, assert_raises,
                             assert_true)
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


def assert_token_is_same_active_and_valid(original_token, token_to_compare):
    assert_equal(original_token, token_to_compare)
    assert_true(token_to_compare.is_valid)
    assert_true(token_to_compare.is_active)


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

        token.extra_data = None
        token.save()
        assert_equal(token.get_extra_data(), None)

    @data_provider('create_user')
    def test_verification_token_expiration_should_be_nullable(self, user):
        token = VerificationToken.objects.deactivate_and_create(user, expiration_in_minutes=None)
        assert_equal(token.expiration_in_minutes, None)

    @data_provider('create_user')
    def test_verification_token_does_not_expire_without_expiration_value(self, user):
        token = VerificationToken.objects.deactivate_and_create(user, expiration_in_minutes=None)
        with freeze_time(timezone.now() + timedelta(days=30*365), tick=True):
            assert_true(token.is_valid)
            assert_true(token.is_active)

    @data_provider('create_user')
    def test_verification_token_get_active_or_create_should_return_existing_active_and_valid_token(self, user):
        created_token = VerificationToken.objects.deactivate_and_create(user, expiration_in_minutes=10)

        with freeze_time(timezone.now(), tick=True):
            obtained_token = VerificationToken.objects.get_active_or_create(user)
            assert_token_is_same_active_and_valid(created_token, obtained_token)

        with freeze_time(timezone.now() + timedelta(minutes=5), tick=True):
            obtained_token = VerificationToken.objects.get_active_or_create(user)
            assert_token_is_same_active_and_valid(created_token, obtained_token)

    @data_provider('create_user')
    def test_verification_token_should_be_found_by_model_class_or_instance(self, user):
        # 2 users of the same content type with tokens created
        user2 = User.objects._create_user('user2', 'user2@test.cz', 'test2')
        token = VerificationToken.objects.deactivate_and_create(user)
        VerificationToken.objects.deactivate_and_create(user2, deactivate_old_tokens=False)

        # another content type object with token created
        group = Group.objects.create(name='authorized_group')
        token_from_group = VerificationToken.objects.deactivate_and_create(group, deactivate_old_tokens=False)

        tokens_by_class = VerificationToken.objects.filter_active_tokens(User)
        assert_equal(tokens_by_class.count(), 2)

        tokens_by_object = VerificationToken.objects.filter_active_tokens(user)
        assert_equal(tokens_by_object.count(), 1)
        assert_token_is_same_active_and_valid(tokens_by_object.first(), token)

        tokens_by_object = VerificationToken.objects.filter_active_tokens(Group)
        assert_equal(tokens_by_object.count(), 1)
        assert_token_is_same_active_and_valid(tokens_by_object.first(), token_from_group)
