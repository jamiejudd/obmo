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
from django.test import Client


def update_due_balances():
    for x in Account.objects.values_list('id',flat=True):
        with transaction.atomic():
            account = Account.objects.select_for_update().get(id=x)
            current_time = timezone.now()
            account.update_balance_due(current_time)
            account.save()

def update_balances():
    for x in Account.objects.values_list('id',flat=True):
        with transaction.atomic():
            event_counter = EventCounter.objects.select_for_update().first() 
            account = Account.objects.get(id=x)
            if (account.balance_due >= constants.UBI_AMOUNT):
                current_time = timezone.now()
                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='BU') #handle integrity error for create
                new_balance_update = BalanceUpdate.objects.create(event=new_event,account=account,amount=constants.UBI_AMOUNT)

                account.balance += constants.UBI_AMOUNT
                account.balance_due -= constants.UBI_AMOUNT
                account.save()

                event_counter.last_event_no += 1
                event_counter.save()


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
                    old_is_good = link.is_good()
                    link.degree += 1
                    link.good = link.is_good()
                    #assert link.zone() == 'Good' or link.zone() == 'Bad'
                    if link.matched_count > 0 and link.is_good() != old_zone:
                        link.settlement_countdown = current_time
                    link.save()
                account.degree = len(links)
                account.good = account.is_good()
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


def do_next_create_challenge_links_if_ready(): #run every few seconds
    next_challenge = Challenge.objects.filter(linked=False).order_by('created').first() 
    if next_challenge is not None and next_challenge.created + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS) < timezone.now():
        getcontext().prec = 999
        t2 = next_challenge.created
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

        challengeid_hex =  format(next_challenge.id, 'x') #"%0.2X" % next_challenge.id '{:02x}'.format(next_challenge.id)
        if len(challengeid_hex) % 2 != 0:
            challengeid_hex = '0'+challengeid_hex
        #print(challengeid_hex)
        random_input_string += challengeid_hex
        prev_accounts = Account.objects.filter(linked=True,suspended=False)
        computed_keys = [(acc.id,(Decimal(int.from_bytes(nacl.hash.sha512(bytes.fromhex(random_input_string+acc.public_key),encoder=nacl.encoding.RawEncoder),byteorder='big'))/Decimal(2**512))**(Decimal(constants.CHALLENGE_LINK_WEIGHTING_PARAMETER)**Decimal(acc.challenge_degree))) for acc in prev_accounts]
        #computed_keys = [(acc,(hash_hex_string_to_u(random_input_string+acc.public_key))**(Decimal(constants.LINK_WEIGHTING_PARAMETER)**Decimal(acc.challenge_degree))) for acc in prev_accounts]

        #links = computed_keys.sort(key = itemgetter(1), reverse = True)[:constants.NUM_CHALLENGE_LINKS]
        links = sorted(computed_keys, key=lambda pair: pair[1], reverse = True)[:constants.NUM_CHALLENGE_LINKS]

        with transaction.atomic():     #inputs: next_acc, links       
            event_counter = EventCounter.objects.select_for_update().first()
            challenge = Challenge.objects.select_for_update().get(id = next_challenge.id) #probly dont need sel4update
            current_time = timezone.now()
            if challenge.linked == False: 
                for linkpair in links:
                    link = Account.objects.get(id = linkpair[0]) #NB WE NEED TO REGET THE LINK INSIDE THE TXN AS IT COULD HAVE CHANGED AND WE WOULD OVERWRITE THAT CHANGE AT LINK.SAVE() #select_for_update()?
                    new_challenge_link = ChallengeLink.objects.create(challenge=challenge,voter=link)
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='CLC') #handle integrity error for create
                    ChallengeLinkCreation.objects.create(event=new_event,challengelink=new_challenge_link)
                    event_counter.last_event_no += 1
                    link.challenge_degree += 1
                    link.save()
                challenge.degree = len(links)
                challenge.good = challenge.is_good()
                challenge.linked = True
                challenge.save()
                event_counter.save()
                assert challenge.degree == len(ChallengeLink.objects.filter(challenge=challenge)), 'created wrong degreeee'
                #print('finished creating links {}'.format(timezone.now()))
                return 'created_challenge_links'
            else:
                #print('finished creating links not done {}'.format(timezone.now()))
                return 'challenge_already_linked' #shouldnt happen if using a single thread for this fn
    else:
        return 'no_challenge_ready'


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

            good_arrows = Arrow.objects.filter(target=next_account,status=1,matched=True,cancelled=False)
            bad_arrows = Arrow.objects.filter(target=next_account,status=-1,matched=True,cancelled=False)

            assert len(good_arrows) == len(bad_arrows)
            #assert next_account.zone() == 'Good' or next_account.zone() == 'Bad'

            if next_account.is_good() == True:
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
            else:
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
            next_account.good = next_account.is_good()
            next_account.save()
            event_counter.save()
            return 'Settled market'
        else:
            return 'No market ready'


def do_next_settle_challenge_mkts_if_ready(): #run every few seconds
    with transaction.atomic():      
        event_counter = EventCounter.objects.select_for_update().first()
        next_challenge = Challenge.objects.filter(matched_count__gte = 1, finished = False, cancelled = False).order_by('settlement_countdown').first() #select_for_update? #.exclude(settlement_countdown = None)
        current_time = timezone.now() 
        if next_challenge is not None and next_challenge.settlement_countdown + timezone.timedelta(seconds = constants.CHALLENGE_SETTLEMENT_TIME) < current_time:
            new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='CS') #handle integrity error for create
            challenge_settlement = ChallengeSettlement.objects.create(event=new_event, challenge=next_challenge)
            event_counter.last_event_no += 1

            good_links = ChallengeLink.objects.filter(challenge=next_challenge, status=1, matched=True, cancelled = False)
            bad_links = ChallengeLink.objects.filter(challenge=next_challenge, status=-1, matched=True, cancelled = False)
            assert len(good_links) == len(bad_links)
            #assert next_challenge.zone() == 'Good' or next_challenge.zone() == 'Bad'

            if next_challenge.is_good() == True:
                for link in good_links:
                    voter = link.voter
                    voter.balance += constants.CHALLENGE_BET_BAD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='CST') #handle integrity error for create
                    ChallengeSettlementTransfer.objects.create(event=new_event,challenge_settlement=challenge_settlement,payee=voter,amount=constants.CHALLENGE_BET_BAD)
                    event_counter.last_event_no += 1
                    voter.save()
                for link in bad_links:
                    voter = link.voter
                    voter.balance -= constants.CHALLENGE_BET_BAD
                    new_event = Event.objects.create(id = event_counter.last_event_no + 1, timestamp = current_time, event_type = 'CST') #handle integrity error for create
                    ChallengeSettlementTransfer.objects.create(event = new_event, challenge_settlement = challenge_settlement, payee = voter, amount = -constants.CHALLENGE_BET_BAD)
                    event_counter.last_event_no += 1
                    voter.save()
            else: 
                print('.............challenge settled-bad.....................')
                challenger = next_challenge.challenger
                challenger.balance += constants.CHALLENGER_REWARD
                new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='CST') #handle integrity error for create
                ChallengeSettlementTransfer.objects.create(event=new_event,challenge_settlement=challenge_settlement,payee=challenger,amount=constants.CHALLENGER_REWARD)
                event_counter.last_event_no += 1
                challenger.save()

                for link in good_links:
                    voter = link.voter
                    voter.balance -= constants.CHALLENGE_BET_GOOD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='CST') #handle integrity error for create
                    ChallengeSettlementTransfer.objects.create(event=new_event,challenge_settlement=challenge_settlement,payee=voter,amount=-constants.CHALLENGE_BET_GOOD)
                    event_counter.last_event_no += 1
                    voter.save()
                for link in bad_links:
                    voter = link.voter
                    voter.balance += constants.CHALLENGE_BET_GOOD
                    new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='CST') #handle integrity error for create
                    ChallengeSettlementTransfer.objects.create(event=new_event,challenge_settlement=challenge_settlement,payee=voter,amount=constants.CHALLENGE_BET_GOOD)
                    event_counter.last_event_no += 1
                    voter.save()

                links1 = ChallengeLink.objects.filter(challenge=next_challenge, status_who=1, matched_who = True, cancelled = False, finished = False)
                links2 = ChallengeLink.objects.filter(challenge=next_challenge, status_who=-1, matched_who = True, cancelled = False, finished = False)

                if next_challenge.net_votes_who >= 0:
                    for link in links1:
                        voter = link.voter
                        voter.balance += constants.CHALLENGE_BET_WHO
                        new_event = Event.objects.create(id=event_counter.last_event_no + 1, timestamp = current_time, event_type = 'CST') #handle integrity error for create
                        ChallengeSettlementTransfer.objects.create(event = new_event, challenge_settlement = challenge_settlement, payee = voter, amount = constants.CHALLENGE_BET_WHO)
                        event_counter.last_event_no += 1
                        voter.save()
                    for link in links2:
                        voter = link.voter
                        voter.balance -= constants.CHALLENGE_BET_WHO
                        new_event = Event.objects.create(id=event_counter.last_event_no + 1, timestamp = current_time, event_type = 'CST') #handle integrity error for create
                        ChallengeSettlementTransfer.objects.create(event = new_event, challenge_settlement = challenge_settlement, payee = voter, amount = -constants.CHALLENGE_BET_WHO)
                        event_counter.last_event_no += 1
                        voter.save()
                    defendant_2 = next_challenge.defendant_2
                    defendant_2.suspend(current_time)
                else:
                    for link in links2:
                        voter = link.voter
                        voter.balance += constants.CHALLENGE_BET_WHO
                        new_event = Event.objects.create(id=event_counter.last_event_no + 1, timestamp = current_time, event_type = 'CST') #handle integrity error for create
                        ChallengeSettlementTransfer.objects.create(event = new_event, challenge_settlement=challenge_settlement, payee = voter,amount=constants.CHALLENGE_BET_WHO)
                        event_counter.last_event_no += 1
                        voter.save()
                    for link in links1:
                        voter = link.voter
                        voter.balance -= constants.CHALLENGE_BET_WHO
                        new_event = Event.objects.create(id=event_counter.last_event_no + 1, timestamp = current_time, event_type = 'CST') #handle integrity error for create
                        ChallengeSettlementTransfer.objects.create(event = new_event, challenge_settlement = challenge_settlement, payee = voter, amount = -constants.CHALLENGE_BET_WHO)
                        event_counter.last_event_no += 1
                        voter.save()
                    defendant_1 = next_challenge.defendant_1
                    defendant_1.suspend(current_time)
                
            next_challenge.finish() 

            # all_links = ChallengeLink.objects.filter(challenge=next_challenge)
            # for link in all_links:
            #     link.finished = True
            #     link.save()
            # next_challenge.finished = True

            # next_challenge.settlement_countdown = None
            # next_challenge.matched_count = 0
            # next_challenge.matched_count_who = 0
            # next_challenge.net_votes = 0
            # next_challenge.net_votes_who = 0

            #next_challenge.save()

            event_counter.save()
            return 'Settled challenge market'
        else:
            return 'No challenge market ready'


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
    res = client.post('/changevote/', data = data)
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
    client = Client()
    res = client.post('/challenge/', data = data)
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
    client = Client()
    res = client.post('/changevote-challenge/', data = data)
    return res






# def update_links():
#     #run update_mkts before update_links as update links may change a mkt that is ready for sttlement
#     getcontext().prec = 999
#     current_time = timezone.now()
#     cutoff_time = current_time - timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
#     finished = False
#     while finished == False:
#         #print('checking accounts.....')
#         accounts = Account.objects.filter(linked=False, registered=True, registered_date__lte=cutoff_time).order_by('registered_date')
#         #print('no of accounts: '+str(len(accounts)))
#         account = Account.objects.filter(linked=False, registered=True, registered_date__lte=cutoff_time).order_by('registered_date').first()  #should it be -reg?
#         if not account:
#             #print('no more accounts')
#             finished = True
#         else:
#             #print('adding new account:  ' + account.public_key)
#             t2 = account.registered_date
#             t1 = t2 - timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)
#             t3 = t2 + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
#             commits = Commitment.objects.select_related('revelation').filter(txn__event__timestamp__gte = t1, txn__event__timestamp__lte = t2)
#             #commits = Commitment.objects.select_related('revelation').filter(Q(Q(txn__event__timestamp__gte=t1) & Q(txn__event__timestamp__lte=t2))).order_by('txn__event__timestamp')
#             #print('using {} commitments'.format(len(commits)))
#             random_input_string = ''
#             for c in commits:
#                 if hasattr(c, 'revelation'):
#                     random_input_string += c.revelation.revealed_value
#                 else:
#                     random_input_string += ''
#                     #print('missing revelation')
#             #print('random string:')
#             #print(random_input_string)
#             random_input_string += account.public_key

#             for acc in Account.objects.filter(linked=True):
#                 random_string = random_input_string + acc.public_key
#                 random_bytes = bytes.fromhex(random_string)
#                 random_number = nacl.hash.sha512(random_bytes, encoder=nacl.encoding.RawEncoder)
#                 random_int = int.from_bytes(random_number, byteorder='big')
#                 u = Decimal(random_int)/Decimal(2**512)
#                 #logu = u.ln()
#                 w = Decimal(constants.LINK_WEIGHTING_PARAMETER)**Decimal(acc.degree)
#                 #kk = w*logu
#                 k = u**w
#                 acc.key = k
#                 #acc.uu = str(u)
#                 #acc.ww = str(w)
#                 #print('u,deg,w,k')
#                 #print(u)
#                 # print('{:f}'.format(acc.degree)+'\n')
#                 # print('{:f}'.format(w)+'\n')
#                 # print('{:f}'.format(k)+'\n')
#                 acc.save()

#             links = Account.objects.filter(linked=True).order_by('-key')[:constants.NUM_LINKS]
#             #print('links has length: '+str(len(links)))
            
#             with transaction.atomic():
#                 event_counter = EventCounter.objects.select_for_update().first()
#                 for link in links:
#                     new_arrow = Arrow.objects.create(source=link,target=account)
#                     new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='AC') #handle integrity error for create
#                     ArrowCreation.objects.create(event=new_event,arrow=new_arrow)
#                     event_counter.last_event_no += 1

#                     new_arrow = Arrow.objects.create(source=account,target=link)
#                     new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='AC') #handle integrity error for create
#                     ArrowCreation.objects.create(event=new_event,arrow=new_arrow)
#                     event_counter.last_event_no += 1

#                     prev_verification_staus = link.verified()
#                     #print(prev_verification_staus)
#                     link.degree += 1
#                     account.degree += 1
#                     #print(link.verified())
#                     if link.verified != prev_verification_staus:
#                         if (prev_verification_staus == True):
#                             elapsed_time = t3 - link.balance_due_last_updated 
#                             # print(elapsed_time.total_seconds())
#                             # print(Decimal(elapsed_time.total_seconds()))
#                             # print(Decimal(constants.UBI_RATE/24/3600))
#                             dividend = Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
#                             link.balance_due += dividend
#                             #target.total_ubi_generated += dividend
#                             link.balance_due_last_updated = t3
#                             #print(dividend)

#                         else: #this wont happen
#                             link.balance_due_last_updated = t3
#                     #account.save()
#                     link.save()
#                 account.linked = True
#                 #account.degree = links.length
#                 account.save()
#                 event_counter.save()







# def update_balances():
    # for x in range(1, Account.objects.count()):
    #     with transaction.atomic():
    #         account = Account.objects.select_for_update().get(pk=x)
    #         if 2*account.net_votes >= account.degree:
    #             account.verified = True
    #         else:
    #             account.verified = False

    #be sure to update verified when ever votes or degree changes, i.e keep veified up to date
    #this code always needs to be run just before we update verified (just the version for a single account tho)


            # #print(current_time)
            # #print(account.zone())
            # if (account.zone() == 'Good'):
            #     elapsed_time = current_time - account.balance_due_last_updated 
            #     dividend = Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
            #     account.balance_due += dividend
            #     #account.total_ubi_generated += dividend
            #     account.balance_due_last_updated = current_time
            #     account.save()
            #     # print(elapsed_time.total_seconds())
            #     # print(Decimal(elapsed_time.total_seconds()))
            #     # print(Decimal(constants.UBI_RATE/24/3600))
            #     # print(dividend)
            #     # print(account.balance_due)
            #     # print(current_time)
            # else:
            #     account.balance_due_last_updated = current_time
            #     account.save()
