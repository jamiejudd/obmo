from django.core.management.base import BaseCommand, CommandError
from core.models import Account, Arrow, Challenge, ChallengeLink, EventCounter
from core.models import Event, Txn, Registration, Transfer, Commitment, Revelation, ArrowUpdate, ChallengeCreation
from core.models import BalanceUpdate, ArrowCreation, MarketSettlement, MarketSettlementTransfer ,ChallengeLinkCreation, ChallengeSettlement, ChallengeSettlementTransfer
from django.utils import timezone

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii

from random import randint
import time
import core.constants as constants
from decimal import *

from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import random, string
from requests import Session

# home_url = 'https://objectivemoney.org'
# photo_path = '/home/jamie/obmo/static/core/images/icon.png'

home_url = 'http://127.0.0.1:8000'
photo_path = 'C:/Users/jamie/Desktop/myprojects/obmo/media/account_photos/pretlogo.jpg'

def register(self):
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    name = ''.join(random.choices(string.ascii_lowercase, k=8)) 
    photo_hash = self.encode(encoder=nacl.encoding.RawEncoder).hex() + '0'*64
    message_string_bytes = bytes('Type:Register,PublicKey:'+username+',SeqNo:'+str(1)+',Name:'+name+',PhotoHash:'+photo_hash, 'utf8')
    data = {}
    data['username'] = username
    data['sender_seq_no'] = 1
    data['name'] = name
    data['password1'] = 'a'
    data['photo_hash'] = photo_hash
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    files = [('photo', ('pretlogo.jpeg', open(photo_path, 'rb'), 'image/jpeg'))]
    client = Session()
    client.get(home_url+'/register/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/register/', data = data, files = files)
    #res = client.get('http://127.0.0.1:8000/register/')
    return res

def transfer(self,sk,amount):
    master = Account.objects.first()
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    recipient_pk = sk.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    message_string_bytes = bytes('Type:Transfer,Sender:'+username+',SeqNo:'+str(master.sequence_next)+',Recipient:'+recipient_pk+',Amount:'+str(amount),'utf8') 
    data = {}
    data['username'] = username
    data['sender_seq_no'] = master.sequence_next
    data['recipient_pk'] = recipient_pk
    data['amount'] = amount
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    client = Session()
    client.get(home_url+'/transfer/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/transfer/', data = data)
    #res = client.get('http://127.0.0.1:8000/transfer/')
    return res

def commit(self,r):
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    account = Account.objects.get(public_key=username)
    b = r.to_bytes(64, byteorder='big')
    h = nacl.hash.sha512(b, encoder=nacl.encoding.RawEncoder)
    message_string_bytes = bytes('Type:Commit,Sender:'+username+',SeqNo:'+str(account.sequence_next)+',Hash:'+h.hex(),'utf8') 
    data = {}
    data['username'] = username
    data['sender_seq_no'] = account.sequence_next
    data['committed_hash'] = h.hex()
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    client = Session()
    client.get(home_url+'/commit/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/commit/', data = data)
    return res

def reveal(self,r):
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    account = Account.objects.get(public_key=username)
    b = r.to_bytes(64, byteorder='big')
    h = nacl.hash.sha512(b, encoder=nacl.encoding.RawEncoder)
    message_string_bytes = bytes('Type:Reveal,Sender:'+username+',SeqNo:'+str(account.sequence_next)+',Value:'+b.hex(),'utf8') 
    data = {}
    data['username'] = username
    data['sender_seq_no'] = account.sequence_next
    data['revealed_value'] = b.hex()
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    client = Session()
    client.get(home_url+'/reveal/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/reveal/', data = data)
    return res

def update_arrow(self,target_pk,arrow_status):
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    account = Account.objects.get(public_key=username)
    message_string_bytes = bytes('Type:ChangeVote,Sender:'+username+',SeqNo:'+str(account.sequence_next)+',Target:'+target_pk+',Vote:'+arrow_status,'utf8') 
    data = {}
    data['username'] = username
    data['sender_seq_no'] = account.sequence_next
    data['target_pk'] = target_pk
    data['arrow_status'] = arrow_status
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    client = Session()
    client.get(home_url+'/changevote/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/changevote/', data = data)
    return res

def create_challenge(self,acc1_pk,acc2_pk):
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    account = Account.objects.get(public_key=username)
    message_string_bytes = bytes('Type:Challenge,Sender:'+username+',SeqNo:'+str(account.sequence_next)+',Account1:'+acc1_pk+',Account2:'+acc2_pk,'utf8') 
    data = {}
    data['username'] = username
    data['sender_seq_no'] = account.sequence_next
    data['account_1'] = acc1_pk
    data['account_2'] = acc2_pk
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    client = Session()
    client.get(home_url+'/challenge/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/challenge/', data = data)
    return res


def update_challengevote(self,challengeid,vote,choice):
    username = self.verify_key.encode(encoder=nacl.encoding.RawEncoder).hex()
    account = Account.objects.get(public_key=username)
    message_string_bytes = bytes('Type:ChangeChallengeVote,Sender:'+username+',SeqNo:'+str(account.sequence_next)+',ChallengeID:'+str(challengeid)+',Vote:'+vote+',Choice:'+choice,'utf8') 
    data = {}
    data['username'] = username
    data['sender_seq_no'] = account.sequence_next
    data['challenge_id'] = challengeid
    data['vote'] = vote
    data['choice'] = choice
    data['signature'] = self.sign(message_string_bytes).signature.hex()
    client = Session()
    client.get(home_url+'/changevote-challenge/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post(home_url+'/changevote-challenge/', data = data)
    return res






# def do_all_tasks():
#     all_tasks_done = False
#     while all_tasks_done == False:
#         next_task = Task.objects.filter(completed = False).order_by("time_due").first()
#         if next_task is not None and next_task.time_due < timezone.now():
#             with transaction.atomic():               
#                 event_counter = EventCounter.objects.select_for_update().first()
#                 current_time = timezone.now()
#                 next_task = Task.objects.filter(completed = False).order_by("time_due").first()
#                 if next_task is not None and next_task.time_due < current_time: #check again since next_task may have changed
#                     assert current_time - next_task.time_due < timezone.timedelta(seconds=3), "did task too slow {}".format(next_task.action)
#                     next_task.doit()
#         else:
#             all_tasks_done = True

# def do_next_task():
#     client = Session()
#     client.get('http://127.0.0.1:8000/donexttask/')
#     csrftoken = client.cookies['csrftoken'] 
#     data = {}
#     data["csrfmiddlewaretoken"] = csrftoken
#     res = client.post('http://127.0.0.1:8000/donexttask/', data = data)
#     return res
