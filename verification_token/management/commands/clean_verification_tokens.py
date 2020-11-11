from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from verification_token.models import VerificationToken


class Command(BaseCommand):

    def handle(self, **options):
        inactive_and_expired_tokens = VerificationToken.objects.filter(
            Q(is_active=False) | Q(expires_at__isnull=False, expires_at__lt=timezone.now())
        )

        self.stdout.write('Will delete {} inactive or expired verification tokens'.format(
            inactive_and_expired_tokens.count())
        )
        deletion_count = inactive_and_expired_tokens.delete()
        self.stdout.write('Deleted {} inactive or expired verification tokens'.format(deletion_count[0]))
        self.stdout.write('{} verification tokens remain in database'.format(VerificationToken.objects.count()))
