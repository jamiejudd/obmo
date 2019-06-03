from django.core.management.base import BaseCommand, CommandError
from core.models import Account,EventCounter,Event,BalanceUpdate

from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from decimal import Decimal
from django.utils import timezone

import core.constants as constants



#update verified
#update balance_due
#update balance, ie send 100 to balance

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

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

        ubi_per_second = Decimal(constants.UBI_RATE/24/3600)
        for x in Account.objects.values_list('id',flat=True):
            with transaction.atomic():
                account = Account.objects.select_for_update().get(id=x)
                current_time = timezone.now()
                if (account.verified == True):
                    elapsed_time = current_time-account.balance_due_last_updated 
                    elapsed_time_seconds = Decimal(elapsed_time.total_seconds())
                    dividend = elapsed_time_seconds*Decimal(0.0011574074)  # 100/24*3600=0.0011574074
                    account.balance_due += dividend
                    #account.total_ubi_generated += dividend
                    account.balance_due_last_updated = current_time
                    account.save()
                else:
                    account.balance_due_last_updated = current_time
                    account.save()
              


        #BALANCE_UPDATE

        amount = constants.UBI_AMOUNT
        for x in range(1, Account.objects.count()+1):
            with transaction.atomic():
                account = Account.objects.select_for_update().get(pk=x)
                if (account.balance_due >= amount):
                    #dividend = 100*(account.dividend_due/100)
                    current_time = timezone.now()
                    event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='BU') #handle integrity error for create
                    new_balance_update = BalanceUpdate.objects.create(event=new_event,account=account,amount=amount)

                    account.balance += amount
                    account.balance_due -= amount
                    account.save()

                    event_counter.last_event_no += 1
                    event_counter.save()




        # for account in Account.objects.all():
        #     with transaction.atomic():
        #         txn_no = TxnNo.objects.select_for_update().get(pk=1)
        #         if (account.verified == true):
        #             account.dividend_due += (timezone.now()-account.last_checkpoint)*0.023
        #             account.last_checkpoint = timezone.now()
        #         elif (account.verified == false):
        #             account.last_checkpoint = timezone.now()
        #         else:
        #             #raise error
        #         account.save()


        #         if (account.dividend_due >= 100):
        #             dividend = 100*(account.dividend_due/100)
        #             last_txn = Transaction.objects.get(txn_no = txn_no.last_txn_no)

        #             new_transaction = Transaction.objects.create(txn_type='U',sender=retailer,receiver=account,amount=dividend, confirmed_at=timezone.now(),hash=)
        #             new_transaction.save()

        #             account.balance += dividend
        #             account.dividend_due -= dividend
        #             account.balance_last_updated = timezone.now()
        #             account.save()

        #             txn_no.last_txn_no += 1
        #             txn_no.save()
