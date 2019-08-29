from django.core.management.base import BaseCommand, CommandError
from core.my_custom_functions import do_next_create_challenge_links_if_ready
class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        do_next_create_challenge_links_if_ready()


