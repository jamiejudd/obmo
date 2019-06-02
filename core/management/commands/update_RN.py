from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Transfer,Registration,ArrowUpdate
from django.utils import timezone


from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii


#we run this at every midnight
#need to check if we need to run this before any txn using rn, i.e register and create challenge and updatelinks
class Command(BaseCommand):
    
    def add_arguments(self, parser):
        pass
        #parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):

        with transaction.atomic():
            event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??


            last_rn = RamdomNumber.objects.last()
            if (last_rn.status == 'Commit'):
            elif (last_rn.status == 'Reveal'):
            else:
            new_random_number = RamdomNumber.objects.create(status='Commit')
            current_time = timezone.now()


            new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='RNE') #handle integrity error for create
            new_random_number_event = RNEvent.objects.create(event=new_event,random_number=new_random_number,action='Creation')
            event_counter.last_event_no += 1
            event_counter.save()



        