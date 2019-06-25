from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,Challenge,ChallengeLink,EventCounter,Event,Txn,Registration, Transfer,Commitment,Revelation,ArrowUpdate,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer,ChallengeLinkCreation
from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from decimal import *
getcontext().prec = 160
from django.utils import timezone
import core.constants as constants
from django.db.models import Q

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
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





