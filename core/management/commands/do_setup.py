from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Registration, Transfer,Commitment,Revelation,ArrowUpdate,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer
from django.utils import timezone
import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii
from django.utils import timezone
from random import randint
import time
import core.constants as constants
from decimal import *
getcontext().prec = 4


import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions

# create EventCounter.objects.create(id=1,last_event_no=0)
# register first account u1, using the special register view
# use u1 to commit and reveal input
# run update_balances to get some money in the system
# send transfers to create new accounts
# register those other accs, use rn to make links
class Command(BaseCommand):    
    def add_arguments(self, parser):
        pass
    #accounts = {}
    #def new_account():

    def handle(self, *args, **options):
        event_counter = EventCounter.objects.create(id=1,last_event_no=0)

        # event_counter = EventCounter.objects.create(id=1,last_event_no=2)

        # print('u1 reg date ' +str(timezone.now()))
        # u1 = Account.objects.create(public_key='8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73',balance=100,registered=True,registered_date=timezone.now(),linked=True,sequence_next=2,name='jffhdfghh')
        
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
        
        # time.sleep(constants.TIMEDELTA_1_HOURS)
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

        # time.sleep(constants.TIMEDELTA_1_HOURS)
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



        # signing_key = nacl.signing.SigningKey.generate()
        # signed = signing_key.sign(b"Attack at Dawn")
        # verify_key = signing_key.verify_key
        # verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

        # print(signing_key)
        # print(verify_key)
        # print(signing_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        # print(verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())




        # pk='e0a23e53ae8b68b85d90234aa10f11f261ed59ff9ae4dea44bb617111ba831c8'
        # pk1='8d6419804ad806b1009603be023401f251399a2226f5936d206babc1f15c0d73'
        # pk2='32be9cb52f64619944ee5406b62de618318124a057e3b8546a58d9270355ff01'
        # U1=[]
        # U2=[]
        # R1=[]
        # R2=[]
        # I1=[]
        # I2=[]
        # c1=0
        # c2=0
        # d1=0
        # d2=0
        # e=0
        # f=0
        # for i in range(100000):
        #     r1 = randint(0, 2**512)
        #     b1 = r1.to_bytes(64, byteorder='big')
        #     x1 = b1.hex()
        #     r2 = randint(0, 2**512)
        #     b2 = r2.to_bytes(64, byteorder='big')
        #     x2 = b2.hex()
        #     random_input_string = ''+x1+x2
        #     random_input_string += pk

        #     random_string1 = random_input_string + pk1
        #     random_bytes1 = bytes.fromhex(random_string1)
        #     random_number1 = nacl.hash.sha512(random_bytes1, encoder=nacl.encoding.RawEncoder)
        #     random_int1 = int.from_bytes(random_number1, byteorder='big')
        #     u1 = Decimal(random_int1)/Decimal(2**512)

        #     random_string2 = random_input_string + pk2
        #     random_bytes2 = bytes.fromhex(random_string2)
        #     random_number2 = nacl.hash.sha512(random_bytes2, encoder=nacl.encoding.RawEncoder)
        #     random_int2 = int.from_bytes(random_number2, byteorder='big')
        #     u2 = Decimal(random_int2)/Decimal(2**512)

        #     if u1<0.01:
        #         c1+=1
        #     if u2<0.01:
        #         c2+=1
        #     if u1>0.99:
        #         d1+=1
        #     if u2>0.99:
        #         d2+=1
        #     if u1<0.01 and u2>0.99:
        #         e+=1
        #     if u1>0.99 and u2<0.01:
        #         f+=1



        # print('c1= '+str(c1))
        # print('c2= '+str(c2))
        # print('d1= '+str(d1))
        # print('d2= '+str(d2))
        # print('e= '+str(e))
        # print('f= '+str(f))


            #R1.append(str(r1))
            #I1.append(str(random_int1))
            #U1.append(str(u1))
            #R2.append(str(r2))
            #I2.append(str(random_int2))
            #U2.append(str(u2))

        # print(R1)
        # print(R2)
        # print(I1)
        # print(I2)
        # print(U1)
        # print(U2)
