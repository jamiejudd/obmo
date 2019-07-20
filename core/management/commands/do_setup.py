from django.core.management.base import BaseCommand, CommandError

from core.models import Account, Arrow, Challenge, ChallengeLink, EventCounter
from core.models import Event, Txn, Registration, Transfer, Commitment, Revelation, ArrowUpdate, ChallengeCreation, ChallengeLinkUpdate
from core.models import BalanceUpdate, ArrowCreation, ChallengeLinkCreation, MarketSettlement, MarketSettlementTransfer

import binascii
from django.utils import timezone
from random import randint
import time
import core.constants as constants
from decimal import *


from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions

import random, string
from requests import Session

import threading
from django.contrib.messages import get_messages
from django.test.utils import setup_test_environment

from core.my_custom_functions import do_next_create_links_if_ready, do_next_settle_mkts_if_ready, do_next_create_challenge_links_if_ready, do_next_settle_challenge_mkts_if_ready
#from core.my_custom_functions import update_arrow, commit, reveal, register, transfer, create_challenge, update_challengevote
from core.my_custom_functions2 import update_arrow, commit, reveal, register, transfer, create_challenge, update_challengevote

# create EventCounter.objects.create(id=1,last_event_no=0)
# register first account u1, using the special register view
# use u1 to commit and reveal input
# run update_balances to get some money in the system
# send transfers to create new accounts
# register those other accs, use rn to make links


def always_do_next_create_links_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(1)
        do_next_create_links_if_ready()

def always_do_next_create_challenge_links_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(1)
        do_next_create_challenge_links_if_ready()

def always_do_next_settle_mkts_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(1)
        do_next_settle_mkts_if_ready()

def always_do_next_settle_challenge_mkts_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(1)
        do_next_settle_challenge_mkts_if_ready()


def create_new_challenges(end_time,sks):
    while timezone.now() < end_time:
        sk = random.choice(sks)
        sk1 = random.choice(sks)
        sk2 = random.choice(sks)
        response = create_challenge(sk,sk1.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex(),sk2.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        if hasattr(response, 'wsgi_request'):
            messages = [msg for msg in get_messages(response.wsgi_request)]
            for message in messages:
                print('CHALLENGE\t'+str(message))
        time.sleep(2)
       

def create_new_accounts(master,sks):
    sk = nacl.signing.SigningKey.generate()
    transfer(master,sk,100)
    for i in range(1,8):
        sk = nacl.signing.SigningKey.generate()
        #print(sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        sks.append(sk)
        response = transfer(master,sk,100)
        if hasattr(response, 'wsgi_request'):
            messages = [msg for msg in get_messages(response.wsgi_request)]
            for message in messages:
                print('TRANSFER\t'+str(message))
        # for c in response.cookies:
        #     print(c.name, c.value)
        #t = transfer(master,i+1,sk,1)
        # t_messages = [msg for msg in get_messages(t.wsgi_request)]
        # for message in t_messages:
        #     print('transfer'+str(i)+':   '+sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()+'    '+str(message))
    return sks

def register_new_accounts(sks):
    for sk in sks:
        response = register(sk)
        time.sleep(0.5)
        #print(response.cookies['messages'].value)
        if hasattr(response, 'wsgi_request'):
            messages = [msg for msg in get_messages(response.wsgi_request)]
            for message in messages:
                print('REGISTER\t'+str(message))
        #if r.context is not None:
            #print(dir(r))
            #print(r.__dict__)
            #print(r.context['form_errors'])

def commit_and_reveal(master,end_time):
    while timezone.now() < end_time:
        r = randint(0, 2**512)
        com = commit(master,r)
        if hasattr(com, 'wsgi_request'):
            com_messages = [msg for msg in get_messages(com.wsgi_request)]
            for message in com_messages:
                print('COMMIT\t\t'+str(message))
        time.sleep(constants.TIMEDELTA_1_HOURS)
        mstr = Account.objects.get(public_key=master.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        #print('commited= '+str(mstr.committed))
        #print('reveal: {}'.format(timezone.now()))
        rev = reveal(master,r)
        if hasattr(rev, 'wsgi_request'):
            rev_messages = [msg for msg in get_messages(rev.wsgi_request)]
            for message in rev_messages:
                print('REVEAL\t\t'+str(message))


def update_arrows(end_time,sks):
    while timezone.now() < end_time:
        sk = random.choice(sks)
        # print(sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        account = Account.objects.get(public_key=sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        #print(account.public_key)
        # if account.key > 1:
        #     print('{:f}'.format(account.key))
        arrow = Arrow.objects.filter(source=account).order_by('?').first()
        if arrow is not None:
            target_pk = arrow.target.public_key
            r = randint(1, 7)
            if r == 1:
                response = update_arrow(sk,target_pk,'Distrust')
            elif r == 2:
                response = update_arrow(sk,target_pk,'Neutral')
            else:
                response = update_arrow(sk,target_pk,'Trust')
            if hasattr(response, 'wsgi_request'):
                messages = [msg for msg in get_messages(response.wsgi_request)]
                for message in messages:
                    print('CHANGEVOTE\t'+str(message))
        time.sleep(0.5)



def update_challengelinks(end_time,sks):
    while timezone.now() < end_time:
        sk = random.choice(sks)
        # print(sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        account = Account.objects.get(public_key=sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        #print(account.public_key)
        # if account.key > 1:
        #     print('{:f}'.format(account.key))
        challengelink = ChallengeLink.objects.filter(voter=account).order_by('?').first()
        if challengelink is not None:
            challenge_id = challengelink.challenge.id
            vote = random.choice(['Trust','Distrust','Neutral'])
            choice = random.choice(['Account1','Account2','Neutral'])
            response = update_challengevote(sk,challenge_id,vote,choice)
            if hasattr(response, 'wsgi_request'):
                messages = [msg for msg in get_messages(response.wsgi_request)]
                for message in messages:
                    print('CHANGECHALLENGEVOTE\t'+str(message))
        time.sleep(1)



class Command(BaseCommand):    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        #setup_test_environment()

        event_counter = EventCounter.objects.create(id=1,last_event_no=0)
        end_time = timezone.now() + timezone.timedelta(seconds=50)
        sks = []
        master = nacl.signing.SigningKey.generate()
        r = register(master)





        # all_messages = [msg for msg in get_messages(r.wsgi_request)]
        # for message in all_messages:
        #     print(str(message))
        # for c in r.cookies:
        #     print(c.name, c.value)
        # print(r.context)
        # print(dir(r))
        #sks.append(master)

        # sk = nacl.signing.SigningKey.generate()
        # transfer(master,sk,1)
        # register(sk)
        # time.sleep(2)
        # update_links()
        # target_pk = sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()

        # while timezone.now() < end_time:
        #     update_arrow(master,target_pk,'Trust')
        #     update_arrow(master,target_pk,'Neutral')
        # update_arrow(master,target_pk,'Trust')
        # while timezone.now() < end_time:
        #     pass
        # update_arrow(master,target_pk,'Neutral')






        thread = threading.Thread(target=create_new_accounts, args=(master, sks))
        thread.start()
        thread.join()

        thread1 = threading.Thread(target=commit_and_reveal, args=(master, end_time,))
        thread2 = threading.Thread(target=register_new_accounts, args=(sks,))
        thread3 = threading.Thread(target=always_do_next_create_links_if_ready, args=(end_time,))
        thread4 = threading.Thread(target=create_new_challenges, args=(end_time,sks,))
        thread5 = threading.Thread(target=always_do_next_create_challenge_links_if_ready, args=(end_time,))

        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()

        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()
 

        time.sleep(14)

        end_time = timezone.now() + timezone.timedelta(seconds=30)

        create_links2 = threading.Thread(target=always_do_next_create_links_if_ready, args=(end_time,))
        create_ch_links2 = threading.Thread(target=always_do_next_create_challenge_links_if_ready, args=(end_time,))

        create_links2.start()
        create_ch_links2.start()
        create_links2.join()
        create_ch_links2.join()




        end_time = timezone.now() + timezone.timedelta(seconds=60)

        thread6 = threading.Thread(target=always_do_next_settle_mkts_if_ready, args=(end_time,))
        thread7 = threading.Thread(target=update_arrows, args=(end_time, sks))
        thread8 = threading.Thread(target=always_do_next_settle_challenge_mkts_if_ready, args=(end_time,))
        thread9 = threading.Thread(target=update_challengelinks, args=(end_time, sks))

        thread6.start()
        thread7.start()
        thread8.start()
        thread9.start()
  





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
        # for i in range(1000000):
        #     r1 = randint(0, 2**512)
        #     b1 = r1.to_bytes(64, byteorder='big')
        #     x1 = b1.hex()
            # r2 = randint(0, 2**512)
            # b2 = r2.to_bytes(64, byteorder='big')
            # x2 = b2.hex()
            #random_input_string = ''+x1+x2
            # random_input_string = ''+x1
            # random_input_string += pk

            # random_string1 = random_input_string + pk1
            # random_bytes1 = bytes.fromhex(random_string1)
            # random_number1 = nacl.hash.sha512(random_bytes1, encoder=nacl.encoding.RawEncoder)
            # random_int1 = int.from_bytes(random_number1, byteorder='big')
            # u1 = Decimal(random_int1)/Decimal(2**512)

            # random_string2 = random_input_string + pk2
            # random_bytes2 = bytes.fromhex(random_string2)
            # random_number2 = nacl.hash.sha512(random_bytes2, encoder=nacl.encoding.RawEncoder)
            # random_int2 = int.from_bytes(random_number2, byteorder='big')
            # u2 = Decimal(random_int2)/Decimal(2**512)

            #if u1<0.0001:
            #    c1+=1
            # if u2<0.01:
            #     c2+=1
            # if u1>0.99:
            #     d1+=1
            # if u2>0.99:
            #     d2+=1
            # if u1<0.01 and u2>0.99:
            #     e+=1
            # if u1>0.99 and u2<0.01:
            #     f+=1



        #print('c1= '+str(c1))
        # print('c2= '+str(c2))
        # print('d1= '+str(d1))
        # print('d2= '+str(d2))
        # print('e= '+str(e))
        # print('f= '+str(f))


        # R1.append(str(r1))
        # I1.append(str(random_int1))
        # U1.append(str(u1))
        # R2.append(str(r2))
        # I2.append(str(random_int2))
        # U2.append(str(u2))

        # print(R1)
        # print(R2)
        # print(I1)
        # print(I2)
        # print(U1)
        # print(U2)
