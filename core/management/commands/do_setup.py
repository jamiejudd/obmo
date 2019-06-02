from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Transfer,Registration,ArrowUpdate
from django.utils import timezone

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii

from django.utils import timezone

# create EventCounter.objects.create(id=1,last_event_no=0)
# register first account u1, using the special register view
# use u1 to commit and reveal input

# run update_balances to get some money in the system
# send transfers to create new accounts
# register those other accs, use rn to make links


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        pass
        #parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        # inital setup
        EventCounter.objects.create(id=1,last_event_no=0)






        # u1 = Account.objects.get(public_key='8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73')
        # u2 = Account.objects.get(public_key='32be9cb52f64619944ee5406b62de618318124a057e3b8546a58d9270355ff01')
        # u3 = Account.objects.get(public_key='e0a23e53ae8b68b85d90234aa10f11f261ed59ff9ae4dea44bb617111ba831c8')

        # accs = [u1,u2,u3]

        # for i in range(len(accs)):
        #     for j in range(i+1, len(accs)):
        #         newarr = Arrow.objects.create(source=accs[i],target=accs[j])
        #         newarr_opp = Arrow.objects.create(source=accs[j],target=accs[i])





        # Account.objects.all().delete()
        # Arrow.objects.all().delete()
        # EventCounter.objects.all().delete()
        # Event.objects.all().delete()
        # Txn.objects.all().delete()
        # Transfer.objects.all().delete()
        # Registration.objects.all().delete()
        # ArrowUpdate.objects.all().delete()

        # initial_user = Account.objects.create(public_key="8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73",balance=0,sequence_next=1)


        # u1 = Account.objects.create(public_key="8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73",balance=0,sequence_next=1)
        # u2 = Account.objects.create(public_key="32be9cb52f64619944ee5406b62de618318124a057e3b8546a58d9270355ff01",balance=100,sequence_next=1)
        # u3 = Account.objects.create(public_key="e0a23e53ae8b68b85d90234aa10f11f261ed59ff9ae4dea44bb617111ba831c8",balance=100,sequence_next=1)


        # current_time = timezone.now()
        # message_string = 'Type:Transfer,Sender:8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73,SeqNo:1,Recipient:32be9cb52f64619944ee5406b62de618318124a057e3b8546a58d9270355ff01,Amount:5'
        # signature = '87c21feb9c3a0d5f1d5ff9ae1e76019728e6af1dfb10092152ac05e20b4da88c67415a43480e455f0e2f390cfeb80c564088e3b01c9e6652e8855b09bd5b940a'                   
        # txn_data = '"TxnNo":"1","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"Genesis"'
        # txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.HexEncoder)
        # amount = 5

        # new_event = Event.objects.create(id=1,timestamp=current_time, event_type='Txn')
        # new_txn = Txn.objects.create(id=1,event=new_event,txn_previous_hash='Genesis',txn_type='Transfer',sender=u1,sender_seq_no=1,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash)
        # new_transfer = Transfer.objects.create(txn=new_txn,recipient=u2,amount=amount)

        # u1.balance -= amount
        # u2.balance += amount
        # u1.sequence_next += 1
        # u1.save()
        # u2.save()
       