from django.core.management.base import BaseCommand, CommandError
from core.my_custom_functions import update_balances

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        update_balances()