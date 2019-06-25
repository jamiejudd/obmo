from django.core.management.base import BaseCommand, CommandError
from core.models import Account,Arrow,EventCounter,Event,Txn,Registration, Transfer,Commitment,Revelation,ArrowUpdate,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer
from django.utils import timezone


from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii

import core.constants as constants


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        current_time = timezone.now()
        cutoff_time = current_time - timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME)
        accounts = Account.objects.filter(settlement_countdown__lte = cutoff_time)
        print(len(accounts))
        for account in accounts:
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??

                new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MU') #handle integrity error for create
                market_settlement = MarketSettlement.objects.create(event=new_event, account=account)
                event_counter.last_event_no += 1

                good_arrows = Arrow.objects.filter(target=account,status=1,matched=True)
                bad_arrows = Arrow.objects.filter(target=account,status=-1,matched=True)

                if len(good_arrows) != len(bad_arrows):
                    print('baderror343')

                print(str(len(good_arrows)))
                print(str(account.zone()))
                if account.zone() == 'Good':
                    for arrow in good_arrows:
                        arrow.source.balance += constants.BET_BAD
                        new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MU') #handle integrity error for create
                        MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=arrow.source,amount=constants.BET_BAD)
                        event_counter.last_event_no += 1
                    for arrow in bad_arrows:
                        arrow.source.balance -= constants.BET_BAD
                        new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MU') #handle integrity error for create
                        MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=arrow.source,amount=constants.BET_BAD)
                        event_counter.last_event_no += 1
                elif account.zone() == 'Bad':
                    for arrow in good_arrows:
                        arrow.source.balance -= constants.BET_GOOD
                        new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MU') #handle integrity error for create
                        MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=arrow.source,amount=constants.BET_GOOD)
                        event_counter.last_event_no += 1
                    for arrow in bad_arrows:
                        arrow.source.balance += constants.BET_GOOD
                        new_event = Event.objects.create(id=event_counter.last_event_no+1, timestamp=current_time, event_type='MU') #handle integrity error for create
                        MarketSettlementTransfer.objects.create(event=new_event,market_settlement=market_settlement,payee=arrow.source,amount=constants.BET_GOOD)
                        event_counter.last_event_no += 1
                else:
                    print('bigsrror223')

                event_counter.save()



        