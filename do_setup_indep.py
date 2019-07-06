from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Registration, Transfer,Commitment,Revelation,ArrowUpdate,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer

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

#from core.my_custom_functions import do_next_create_links_if_ready, do_next_settle_mkts_if_ready, update_arrow, commit, reveal, register, transfer, create_challenge
from core.my_custom_functions2 import do_next_create_links_if_ready, do_next_settle_mkts_if_ready, update_arrow, commit, reveal, register, transfer, create_challenge

# create EventCounter.objects.create(id=1,last_event_no=0)
# register first account u1, using the special register view
# use u1 to commit and reveal input
# run update_balances to get some money in the system
# send transfers to create new accounts
# register those other accs, use rn to make links


def always_do_next_create_links_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(0.1)
        do_next_create_links_if_ready()

def always_do_next_create_challenge_links_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(1)
        do_next_create_challenge_links_if_ready()

def always_do_next_settle_mkts_if_ready(end_time):
    while timezone.now() < end_time:
        time.sleep(1)
        do_next_settle_mkts_if_ready()


def create_new_challenges(end_time,sks):
    while timezone.now() < end_time:
        sk = random.choice(sks)
        sk1 = random.choice(sks)
        sk2 = random.choice(sks)
        response = create_challenge(sk,sk1.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex(),sk2.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        # messages = [msg for msg in get_messages(response.wsgi_request)]
        # for message in messages:
        #     print('CHALLENGE '+str(message))
        time.sleep(0.5)
       

def create_new_accounts(master,sks):
    sk = nacl.signing.SigningKey.generate()
    transfer(master,sk,1)
    for i in range(1,18):
        sk = nacl.signing.SigningKey.generate()
        #print(sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        sks.append(sk)
        response = transfer(master,sk,1)
        # for c in response.cookies:
        #     print(c.name, c.value)
        #t = transfer(master,i+1,sk,1)
        # t_messages = [msg for msg in get_messages(t.wsgi_request)]
        # for message in t_messages:
        #     print('transfer'+str(i)+':   '+sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()+'    '+str(message))
    return sks

def register_new_accounts(sks):
    for sk in sks:
        print('register: {}'.format(timezone.now()))
        response = register(sk)
        time.sleep(0.5)
        #print(response.cookies['messages'].value)
        # r_messages = [msg for msg in get_messages(r.wsgi_request)]
        # for message in r_messages:
        #     print('register:   '+sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()+'    '+str(message))
        #if r.context is not None:
            #print(dir(r))
            #print(r.__dict__)
            #print(r.context['form_errors'])

def commit_and_reveal(master,end_time):
    while timezone.now() < end_time:
        r = randint(0, 2**512)
        print('commit: {}'.format(timezone.now()))
        com = commit(master,r)
        # com_messages = [msg for msg in get_messages(com.wsgi_request)]
        # for message in com_messages:
        #     print('commit:     '+str(message))
        time.sleep(constants.TIMEDELTA_1_HOURS)
        mstr = Account.objects.get(public_key=master.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        #print('commited= '+str(mstr.committed))
        print('reveal: {}'.format(timezone.now()))
        rev = reveal(master,r)
        # rev_messages = [msg for msg in get_messages(rev.wsgi_request)]
        # for message in rev_messages:
        #     print('reveal:     '+str(message))


def update_arrows(end_time,sks):
    while timezone.now() < end_time:
        sk = random.choice(sks)
        # print(sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        account = Account.objects.get(public_key=sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
        #print(account.public_key)
        # if account.key > 1:
        #     print('{:f}'.format(account.key))
        target_pk = Arrow.objects.filter(source=account).order_by('?').first().target.public_key
        r = randint(1, 11)
        if r == 1:
            update_arrow(sk,target_pk,'Distrust')
        elif r == 2:
            update_arrow(sk,target_pk,'Neutral')
        else:
            update_arrow(sk,target_pk,'Trust')
        time.sleep(0.5)




event_counter = EventCounter.objects.create(id=1,last_event_no=0)
end_time = timezone.now() + timezone.timedelta(seconds=50)
end_time2 = timezone.now() + timezone.timedelta(seconds=70)
sks = []
master = nacl.signing.SigningKey.generate()
#print(master.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex())
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
# thread5.start()


thread1.join()
thread2.join()
thread3.join()


time.sleep(2)

thread6 = threading.Thread(target=always_do_next_settle_mkts_if_ready, args=(end_time2,))
thread7 = threading.Thread(target=update_arrows, args=(end_time2, sks))

thread6.start()
thread7.start()
