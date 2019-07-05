from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Registration, Transfer,Commitment,Revelation,ArrowUpdate,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer
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

def do_next_create_links_if_ready(): #run every few seconds
    next_account = Account.objects.filter(linked=False, registered=True, suspended=False).order_by('registered_date').first() 
    if next_account is not None and next_account.registered_date + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS) < timezone.now():
        getcontext().prec = 999
        t2 = next_account.registered_date
        t1 = t2 - timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)
        assert timezone.now() > t2 + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
        commits = Commitment.objects.select_related('revelation').filter(txn__event__timestamp__gte = t1, txn__event__timestamp__lte = t2).order_by('txn__event__timestamp')
        #print('using {} commitments'.format(len(commits)))
        random_input_string = ''
        for c in commits:
            if hasattr(c, 'revelation'):
                random_input_string += c.revelation.revealed_value
            else:
                random_input_string += ''
                print('missing revelation')
        random_input_string += next_account.public_key
        prev_accounts = Account.objects.filter(linked=True,suspended=False)
        computed_keys = [(acc.id,(Decimal(int.from_bytes(nacl.hash.sha512(bytes.fromhex(random_input_string+acc.public_key),encoder=nacl.encoding.RawEncoder),byteorder='big'))/Decimal(2**512))**(Decimal(constants.LINK_WEIGHTING_PARAMETER)**Decimal(acc.degree))) for acc in prev_accounts]
        #computed_keys = [(acc,(hash_hex_string_to_u(random_input_string+acc.public_key))**(Decimal(constants.LINK_WEIGHTING_PARAMETER)**Decimal(acc.degree))) for acc in prev_accounts]

        #links = computed_keys.sort(key = itemgetter(1), reverse = True)[:constants.NUM_LINKS]
        links = sorted(computed_keys, key=lambda pair: pair[1], reverse = True)[:constants.NUM_LINKS]

        with transaction.atomic():     #inputs: next_acc, links       
            event_counter = EventCounter.objects.select_for_update().first()
            account = Account.objects.select_for_update().get(id = next_account.id) #probly dont need sel4update
            current_time = timezone.now()
            if account.linked == False and account.suspended == False: 
                for linkpair in links:
                    link = Account.objects.get(id = linkpair[0]) #NB WE NEED TO REGET THE LINK INSIDE THE TXN AS IT COULD HAVE CHANGED AND WE WOULD OVERWRITE THAT CHANGE AT LINK.SAVE() #select_for_update()?
                    new_arrow = Arrow.objects.create(source=link,target=account)
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='AC') #handle integrity error for create
                    ArrowCreation.objects.create(event=new_event,arrow=new_arrow)
                    event_counter.last_event_no += 1
                    new_arrow = Arrow.objects.create(source=account,target=link)
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='AC') #handle integrity error for create
                    ArrowCreation.objects.create(event=new_event,arrow=new_arrow)
                    event_counter.last_event_no += 1
                    link.update_balance_due(current_time) #as verfiied may be about to change
                    old_zone = link.zone()
                    link.degree += 1
                    assert link.zone() == 'Good' or link.zone() == 'Bad'
                    if link.matched_count > 0 and link.zone() != old_zone:
                        link.settlement_countdown = current_time
                    link.save()
                account.degree = len(links)
                account.linked = True
                account.save()
                event_counter.save()
                assert account.degree == len(Arrow.objects.filter(source=account)), 'created wrong degreeee'
                #print('finished creating links {}'.format(timezone.now()))
                return 'created_links'
            else:
                #print('finished creating links not done {}'.format(timezone.now()))
                return 'already_linked' #shouldnt happen if using a single thread for this fn
    else:
        return 'no_acc_ready'


def do_next_settle_mkts_if_ready(): #run every few seconds
    with transaction.atomic():      
        event_counter = EventCounter.objects.select_for_update().first()
        next_account = Account.objects.filter(matched_count__gte = 1, registered = True, suspended = False).exclude(settlement_countdown = None).order_by('settlement_countdown').first() #select_for_update?
        current_time = timezone.now() 
        if next_account is not None and next_account.settlement_countdown + timezone.timedelta(seconds = constants.MARKET_SETTLEMENT_TIME) < current_time:
            new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MS') #handle integrity error for create
            market_settlement = MarketSettlement.objects.create(event=new_event, account=next_account)
            event_counter.last_event_no += 1

            next_account.settlement_countdown = None
            next_account.matched_count = 0

            good_arrows = Arrow.objects.filter(target=next_account,status=1,matched=True)
            bad_arrows = Arrow.objects.filter(target=next_account,status=-1,matched=True)

            assert len(good_arrows) == len(bad_arrows)
            assert next_account.zone() == 'Good' or next_account.zone() == 'Bad'

            if next_account.zone() == 'Good':
                next_account.net_votes += len(good_arrows)
                for arrow in good_arrows:
                    arrow.matched = False
                    source = arrow.source
                    source.balance += constants.BET_BAD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MST') #handle integrity error for create
                    MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=source,amount=constants.BET_BAD)
                    event_counter.last_event_no += 1
                    source.save()
                    arrow.save()
                for arrow in bad_arrows:
                    arrow.status = 0
                    #arrow.position = None
                    arrow.matched = False
                    source = arrow.source
                    source.balance -= constants.BET_BAD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MST') #handle integrity error for create
                    MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=source,amount=-constants.BET_BAD)
                    event_counter.last_event_no += 1
                    source.save()
                    arrow.save()
            elif next_account.zone() == 'Bad':
                next_account.net_votes -= len(good_arrows)
                for arrow in good_arrows:
                    arrow.status = 0
                    #arrow.position = None
                    arrow.matched = False
                    source = arrow.source
                    source.balance -= constants.BET_GOOD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MST') #handle integrity error for create
                    MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=source,amount=-constants.BET_GOOD)
                    event_counter.last_event_no += 1
                    source.save()
                    arrow.save()
                for arrow in bad_arrows:
                    arrow.matched = False
                    source = arrow.source
                    source.balance += constants.BET_GOOD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MST') #handle integrity error for create
                    MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=source,amount=constants.BET_GOOD)
                    event_counter.last_event_no += 1
                    source.save()
                    arrow.save()
            else:
                print('bigsrror223')
            next_account.save()
            event_counter.save()
            return 'settled_mkt'
        else:
            return 'no_mkt_ready'
         

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
    files = [('photo', ('pretlogo.jpeg', open('C:/Users/jamie/Desktop/myprojects/obmo/media/account_photos/pretlogo.jpg', 'rb'), 'image/jpeg'))]
    client = Session()
    client.get('http://127.0.0.1:8000/register/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post('http://127.0.0.1:8000/register/', data = data, files = files)
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
    client.get('http://127.0.0.1:8000/transfer/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post('http://127.0.0.1:8000/transfer/', data = data)
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
    client.get('http://127.0.0.1:8000/commit/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post('http://127.0.0.1:8000/commit/', data = data)
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
    client.get('http://127.0.0.1:8000/reveal/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post('http://127.0.0.1:8000/reveal/', data = data)
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
    client.get('http://127.0.0.1:8000/changevote/')
    csrftoken = client.cookies['csrftoken'] 
    data["csrfmiddlewaretoken"] = csrftoken
    res = client.post('http://127.0.0.1:8000/changevote/', data = data)
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
