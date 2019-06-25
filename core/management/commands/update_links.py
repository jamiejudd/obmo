from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Registration, Transfer,Commitment,Revelation,ArrowUpdate,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer
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
            print('checking accounts.....')
            accounts = Account.objects.filter(linked=False, registered=True, registered_date__lte=cutoff_time).order_by('registered_date')
            print('no of accounts: '+str(len(accounts)))
            account = Account.objects.filter(linked=False, registered=True, registered_date__lte=cutoff_time).order_by('registered_date').first()
            if not account:
                print('no more accounts')
                finished = True
            else:
                print('adding new account:  ' + account.public_key)
                t2 = account.registered_date
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
                random_input_string += account.public_key

                for acc in Account.objects.filter(linked=True):
                    random_string = random_input_string + acc.public_key
                    random_bytes = bytes.fromhex(random_string)
                    random_number = nacl.hash.sha512(random_bytes, encoder=nacl.encoding.RawEncoder)
                    random_int = int.from_bytes(random_number, byteorder='big')
                    u = Decimal(random_int)/Decimal(2**512)
                    w = Decimal('1.3')**Decimal(acc.degree)
                    k = u**w
                    acc.key = k
                    # print('u,deg,w,k')
                    # print(u)
                    # print(acc.degree)
                    # print(w)
                    # print(k)
                    acc.save()

                links = Account.objects.filter(linked=True).order_by('key')[:15]
                print('links has length: '+str(len(links)))
                
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
                        print(prev_verification_staus)
                        link.degree += 1
                        account.degree += 1
                        print(link.verified())
                        if link.verified != prev_verification_staus:
                            if (prev_verification_staus == True):
                                elapsed_time = t3 - link.balance_due_last_updated 
                                print('hudf')
                                print(elapsed_time.total_seconds())
                                print(Decimal(elapsed_time.total_seconds()))
                                print(Decimal(constants.UBI_RATE/24/3600))
                                dividend = Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
                                link.balance_due += dividend
                                #target.total_ubi_generated += dividend
                                link.balance_due_last_updated = t3
                                print(dividend)

                            else: #this wont happen
                                link.balance_due_last_updated = t3
                        #account.save()
                        link.save()
                    account.linked = True
                    #account.degree = links.length
                    account.save()
                    event_counter.save()





