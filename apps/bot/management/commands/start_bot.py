from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start Bot"

    def handle(self, *args, **options):...