from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Transfer,Registration,ArrowUpdate,Commitment,Revelation
from django.utils import timezone
import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii
from django.utils import timezone
from random import randint
import time
# create EventCounter.objects.create(id=1,last_event_no=0)
# register first account u1, using the special register view
# use u1 to commit and reveal input
# run update_balances to get some money in the system
# send transfers to create new accounts
# register those other accs, use rn to make links
class Command(BaseCommand):    
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        event_counter = EventCounter.objects.create(id=1,last_event_no=0)
        
        # print('u1 reg date ' +str(timezone.now()))
        # u1 = Account.objects.create(public_key='8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73',balance=100,registered=True,registered_date=timezone.now(),verified=True,linked=True,sequence_next=2,name='jffhdfghh')
        
        # r1 = randint(0, 2**512)
        # b1 = r1.to_bytes(64, byteorder='big')
        # h1 = nacl.hash.sha512(b1, encoder=nacl.encoding.RawEncoder)
        # current_time = timezone.now()
        # new_event = Event.objects.create(timestamp=current_time,event_type='Txn')
        # new_txn = Txn.objects.create(event=new_event,txn_previous_hash='',txn_type='Commitment',sender=u1,sender_seq_no=1,txn_message='',signature='',txn_data='',txn_hash='')
        # new_commitment = Commitment.objects.create(txn=new_txn,committed_hash=h1.hex())
        # u1.committed = True
        # u1.committed_time = current_time
        # u1.committed_hash = h1.hex()
        # u1.save()

        # print('u2 reg date ' +str(timezone.now()))
        # u2 = Account.objects.create(public_key='32be9cb52f64619944ee5406b62de618318124a057e3b8546a58d9270355ff01',balance=100,registered=True,registered_date=timezone.now(),sequence_next=2,name='fefefehh')
        
        # time.sleep(5)
        # commitment = Commitment.objects.filter(txn__sender = u1).last()
        # new_event = Event.objects.create(timestamp=timezone.now(), event_type='Txn') #handle integrity error for create
        # new_txn = Txn.objects.create(event=new_event,txn_previous_hash='',txn_type='Revelation',sender=u1,sender_seq_no=1,txn_message='',signature='',txn_data='',txn_hash='')
        # new_revelation = Revelation.objects.create(txn=new_txn,commitment=commitment,revealed_value=b1.hex())
        # u1.committed = False
        # u1.save()

        # r1 = randint(0, 2**512)
        # b1 = r1.to_bytes(64, byteorder='big')
        # h1 = nacl.hash.sha512(b1, encoder=nacl.encoding.RawEncoder)
        # current_time = timezone.now()
        # new_event = Event.objects.create(timestamp=current_time,event_type='Txn')
        # new_txn = Txn.objects.create(event=new_event,txn_previous_hash='',txn_type='Commitment',sender=u1,sender_seq_no=1,txn_message='',signature='',txn_data='',txn_hash='')
        # new_commitment = Commitment.objects.create(txn=new_txn,committed_hash=h1.hex())
        # u1.committed = True
        # u1.committed_time = current_time
        # u1.committed_hash = h1.hex()
        # u1.save()


        # r2 = randint(0, 2**512)
        # b2 = r2.to_bytes(64, byteorder='big')
        # h2 = nacl.hash.sha512(b2, encoder=nacl.encoding.RawEncoder)
        # current_time = timezone.now()
        # new_event = Event.objects.create(timestamp=current_time,event_type='Txn')
        # new_txn = Txn.objects.create(event=new_event,txn_previous_hash='',txn_type='Commitment',sender=u2,sender_seq_no=1,txn_message='',signature='',txn_data='',txn_hash='')
        # new_commitment = Commitment.objects.create(txn=new_txn,committed_hash=h2.hex())
        # u2.committed = True
        # u2.committed_time = current_time
        # u2.committed_hash = h2.hex()
        # u2.save()
        # print('u3 reg date ' +str(timezone.now()))
        # u3 = Account.objects.create(public_key='e0a23e53ae8b68b85d90234aa10f11f261ed59ff9ae4dea44bb617111ba831c8',registered=True,registered_date=timezone.now(),sequence_next=2,name='fefefehh')

        # time.sleep(5)
        # commitment = Commitment.objects.filter(txn__sender = u1).last()
        # new_event = Event.objects.create(timestamp=timezone.now(), event_type='Txn') #handle integrity error for create
        # new_txn = Txn.objects.create(event=new_event,txn_previous_hash='',txn_type='Revelation',sender=u1,sender_seq_no=1,txn_message='',signature='',txn_data='',txn_hash='')
        # new_revelation = Revelation.objects.create(txn=new_txn,commitment=commitment,revealed_value=b1.hex())
        # u1.committed = False
        # u1.save()

        # commitment = Commitment.objects.filter(txn__sender = u2).last()
        # new_event = Event.objects.create(timestamp=timezone.now(), event_type='Txn') #handle integrity error for create
        # new_txn = Txn.objects.create(event=new_event,txn_previous_hash='',txn_type='Revelation',sender=u2,sender_seq_no=1,txn_message='',signature='',txn_data='',txn_hash='')
        # new_revelation = Revelation.objects.create(txn=new_txn,commitment=commitment,revealed_value=b2.hex())
        # u2.committed = False
        # u2.save()