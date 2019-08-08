from django.core.management.base import BaseCommand, CommandError
from core.models import EventCounter

class Command(BaseCommand):    
    def add_arguments(self, parser):
        pass
        
    def handle(self, *args, **options):
        event_counter = EventCounter.objects.create(id=1,last_event_no=0)