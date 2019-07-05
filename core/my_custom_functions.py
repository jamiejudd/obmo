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
from django.test import Client



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
    data['photo'] = open('C:/Users/jamie/Desktop/myprojects/obmo/media/account_photos/pretlogo.jpg', "rb")
    client = Client()
    res = client.post('/register/', data = data)
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
    client = Client()
    res = client.post('/transfer/', data = data)
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
    client = Client()
    res = client.post('/commit/', data = data)
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
    client = Client()
    res = client.post('/reveal/', data = data)
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
    client = Client()
    res = client.post('http://127.0.0.1:8000/changevote/', data = data)
    return res


def update_links():
    #run update_mkts before update_links as update links may change a mkt that is ready for sttlement
    getcontext().prec = 999
    current_time = timezone.now()
    cutoff_time = current_time - timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
    finished = False
    while finished == False:
        #print('checking accounts.....')
        accounts = Account.objects.filter(linked=False, registered=True, registered_date__lte=cutoff_time).order_by('registered_date')
        #print('no of accounts: '+str(len(accounts)))
        account = Account.objects.filter(linked=False, registered=True, registered_date__lte=cutoff_time).order_by('registered_date').first()  #should it be -reg?
        if not account:
            #print('no more accounts')
            finished = True
        else:
            #print('adding new account:  ' + account.public_key)
            t2 = account.registered_date
            t1 = t2 - timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)
            t3 = t2 + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
            commits = Commitment.objects.select_related('revelation').filter(txn__event__timestamp__gte = t1, txn__event__timestamp__lte = t2)
            #commits = Commitment.objects.select_related('revelation').filter(Q(Q(txn__event__timestamp__gte=t1) & Q(txn__event__timestamp__lte=t2))).order_by('txn__event__timestamp')
            #print('using {} commitments'.format(len(commits)))
            random_input_string = ''
            for c in commits:
                if hasattr(c, 'revelation'):
                    random_input_string += c.revelation.revealed_value
                else:
                    random_input_string += ''
                    #print('missing revelation')
            #print('random string:')
            #print(random_input_string)
            random_input_string += account.public_key

            for acc in Account.objects.filter(linked=True):
                random_string = random_input_string + acc.public_key
                random_bytes = bytes.fromhex(random_string)
                random_number = nacl.hash.sha512(random_bytes, encoder=nacl.encoding.RawEncoder)
                random_int = int.from_bytes(random_number, byteorder='big')
                u = Decimal(random_int)/Decimal(2**512)
                #logu = u.ln()
                w = Decimal(constants.LINK_WEIGHTING_PARAMETER)**Decimal(acc.degree)
                #kk = w*logu
                k = u**w
                acc.key = k
                #acc.uu = str(u)
                #acc.ww = str(w)
                #print('u,deg,w,k')
                #print(u)
                # print('{:f}'.format(acc.degree)+'\n')
                # print('{:f}'.format(w)+'\n')
                # print('{:f}'.format(k)+'\n')
                acc.save()

            links = Account.objects.filter(linked=True).order_by('-key')[:constants.NUM_LINKS]
            #print('links has length: '+str(len(links)))
            
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()
                for link in links:
                    new_arrow = Arrow.objects.create(source=link,target=account)
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='AC') #handle integrity error for create
                    ArrowCreation.objects.create(event=new_event,arrow=new_arrow)
                    event_counter.last_event_no += 1

                    new_arrow = Arrow.objects.create(source=account,target=link)
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='AC') #handle integrity error for create
                    ArrowCreation.objects.create(event=new_event,arrow=new_arrow)
                    event_counter.last_event_no += 1

                    prev_verification_staus = link.verified()
                    #print(prev_verification_staus)
                    link.degree += 1
                    account.degree += 1
                    #print(link.verified())
                    if link.verified != prev_verification_staus:
                        if (prev_verification_staus == True):
                            elapsed_time = t3 - link.balance_due_last_updated 
                            # print(elapsed_time.total_seconds())
                            # print(Decimal(elapsed_time.total_seconds()))
                            # print(Decimal(constants.UBI_RATE/24/3600))
                            dividend = Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
                            link.balance_due += dividend
                            #target.total_ubi_generated += dividend
                            link.balance_due_last_updated = t3
                            #print(dividend)

                        else: #this wont happen
                            link.balance_due_last_updated = t3
                    #account.save()
                    link.save()
                account.linked = True
                #account.degree = links.length
                account.save()
                event_counter.save()

def update_mkts():
    current_time = timezone.now()
    cutoff_time = current_time - timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME)
    accounts = Account.objects.filter(matched_count__gte = 1, settlement_countdown__lte = cutoff_time)
    print(len(accounts))
    for account in accounts:
        with transaction.atomic():
            event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??

            new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MS') #handle integrity error for create
            market_settlement = MarketSettlement.objects.create(event=new_event, account=account)
            event_counter.last_event_no += 1

            account.settlement_countdown = None
            account.matched_count = 0

            good_arrows = Arrow.objects.filter(target=account,status=1,matched=True)
            bad_arrows = Arrow.objects.filter(target=account,status=-1,matched=True)

            if len(good_arrows) != len(bad_arrows):
                print('baderror343')

            print(str(len(good_arrows)))
            print(str(account.zone()))
            if account.zone() == 'Good':
                account.net_votes += len(good_arrows)
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
            elif account.zone() == 'Bad':
                account.net_votes -= len(good_arrows)
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
            account.save()
            event_counter.save()



def create_challenge_links():
    #run update_mkts before update_links as update links may change a mkt that is ready for sttlement
    current_time = timezone.now()
    cutoff_time = current_time - timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
    finished = False
    while finished == False:
        print('checking challenges.....')
        challenges = Challenge.objects.filter(linked=False, created__lte=cutoff_time).order_by('created')
        print('no of challenges: '+str(len(challenges)))
        challenge = Challenge.objects.filter(linked=False, created__lte=cutoff_time).order_by('created').first()
        if not challenge:
            print('no more challenges')
            finished = True
        else:
            print('linking new challenge:  ' + str(challenge.id))
            t2 = challenge.created
            t1 = t2 - timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)
            t3 = t2 + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
            commits = Commitment.objects.select_related('revelation').filter(txn__event__timestamp__gte = t1, txn__event__timestamp__lte = t2)
            #commits = Commitment.objects.select_related('revelation').filter(Q(Q(txn__event__timestamp__gte=t1) & Q(txn__event__timestamp__lte=t2))).order_by('txn__event__timestamp')
            print('using {} commitments'.format(len(commits)))
            random_input_string = ''
            for c in commits:
                if hasattr(c, 'revelation'):
                    random_input_string += c.revelation.revealed_value
                else:
                    random_input_string += ''
                    print('missing revelation')
            print('random string:')
            print(random_input_string)
            random_input_string += challenge.defendant_1.public_key
            random_input_string += challenge.defendant_2.public_key

            for acc in Account.objects.filter(registered=True):
                random_string = random_input_string + acc.public_key
                random_bytes = bytes.fromhex(random_string)
                random_number = nacl.hash.sha512(random_bytes, encoder=nacl.encoding.RawEncoder)
                random_int = int.from_bytes(random_number, byteorder='big')
                u = Decimal(random_int)/Decimal(2**512)
                w = Decimal('10')**Decimal(acc.chalenges_degree)
                k = u**w
                acc.chalenges_key = k
                # print('u,deg,w,k')
                # print(u)
                # print(acc.chalenges_degree)
                # print(w)
                # print(k)
                acc.save()

            links = Account.objects.filter(registered=True).order_by('chalenges_key')[:constants.NUM_CHALLENGE_LINKS]
            print('links has length: '+str(len(links)))
            
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()
                for link in links:
                    new_challengelink = ChallengeLink.objects.create(challenge=challenge,voter=link)
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='CLC') #handle integrity error for create
                    ChallengeLinkCreation.objects.create(event=new_event,challengelink=new_challengelink)
                    event_counter.last_event_no += 1

                    link.chalenges_degree += 1
                    challenge.degree += 1
                    link.save()
                challenge.linked = True
                #account.degree = links.length
                challenge.save()
                event_counter.save()




def update_balances():
    # for x in range(1, Account.objects.count()):
    #     with transaction.atomic():
    #         account = Account.objects.select_for_update().get(pk=x)
    #         if 2*account.net_votes >= account.degree:
    #             account.verified = True
    #         else:
    #             account.verified = False

    #be sure to update verified when ever votes or degree changes, i.e keep veified up to date
    #this code always needs to be run just before we update verified (just the version for a single account tho)

    #BALANCE_DUE_UPDATE ll
    for x in Account.objects.values_list('id',flat=True):
        with transaction.atomic():
            account = Account.objects.select_for_update().get(id=x)
            #print(account.balance_due_last_updated)
            current_time = timezone.now()
            #print(current_time)
            #print(account.zone())
            if (account.zone() == 'Good'):
                elapsed_time = current_time - account.balance_due_last_updated 
                dividend = Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
                account.balance_due += dividend
                #account.total_ubi_generated += dividend
                account.balance_due_last_updated = current_time
                account.save()
                # print(elapsed_time.total_seconds())
                # print(Decimal(elapsed_time.total_seconds()))
                # print(Decimal(constants.UBI_RATE/24/3600))
                # print(dividend)
                # print(account.balance_due)
                # print(current_time)
            else:
                account.balance_due_last_updated = current_time
                account.save()
    #BALANCE_UPDATE
    for x in range(1, Account.objects.count()+1):
        with transaction.atomic():
            event_counter = EventCounter.objects.select_for_update().first() 
            account = Account.objects.get(pk=x)
            if (account.balance_due >= constants.UBI_AMOUNT):
                #dividend = 100*(account.dividend_due/100)
                current_time = timezone.now()
                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='BU') #handle integrity error for create
                new_balance_update = BalanceUpdate.objects.create(event=new_event,account=account,amount=constants.UBI_AMOUNT)

                account.balance += constants.UBI_AMOUNT
                account.balance_due -= constants.UBI_AMOUNT
                account.save()

                event_counter.last_event_no += 1
                event_counter.save()



def do_next_task_if_ready(): #run every few seconds
    next_task = Task.objects.filter(completed = False).order_by("time_due").first()
    if next_task is not None and next_task.time_due < timezone.now():
        with transaction.atomic():               
            event_counter = EventCounter.objects.select_for_update().first()
            current_time = timezone.now()
            next_task = Task.objects.filter(completed = False).order_by("time_due").first()
            if next_task is not None and next_task.time_due < current_time: #check again since next_task may have changed
                assert current_time - next_task.time_due < timezone.timedelta(seconds=4), "did task too late {}".format(next_task.account.id) 
                next_task.doit()


def do_all_tasks():
    all_tasks_done = False
    while all_tasks_done == False:
        next_task = Task.objects.filter(completed = False).order_by("time_due").first()
        if next_task is not None and next_task.time_due < timezone.now():
            with transaction.atomic():               
                event_counter = EventCounter.objects.select_for_update().first()
                current_time = timezone.now()
                next_task = Task.objects.filter(completed = False).order_by("time_due").first()
                if next_task is not None and next_task.time_due < current_time: #check again since next_task may have changed
                    assert current_time - next_task.time_due < timezone.timedelta(seconds=3), "did task too slow {}".format(next_task.action)
                    next_task.doit()
        else:
            all_tasks_done = True
