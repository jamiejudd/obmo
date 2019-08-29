from django.core.management.base import BaseCommand, CommandError
from core.my_custom_functions import do_next_settle_mkts_if_ready

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        do_next_settle_mkts_if_ready()