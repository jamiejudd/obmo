from django.core.management.base import BaseCommand, CommandError
from divers.models import Account,Transaction,
from decimal import Decimal
#import datetime 
from django.utils import timezone


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('public_key', nargs='+', type=str)
        parser.add_argument('--balance', type=int)

    #def handle(self, *args, **options):





'''

        for account in Account.objects.all():
            with transaction.atomic():
                txn_no = TxnNo.objects.select_for_update().get(pk=1)
                if (account.verified == true):
                    account.dividend_due += (timezone.now()-account.last_checkpoint)*0.023
                    account.last_checkpoint = timezone.now()
                elif (account.verified == false):
                    account.last_checkpoint = timezone.now()
                else:
                    #raise error
                account.save()


                if (account.dividend_due >= 100):
                    dividend = 100*(account.dividend_due/100)
                    last_txn = Transaction.objects.get(txn_no = txn_no.last_txn_no)

                    new_transaction = Transaction.objects.create(txn_type='U',sender=retailer,receiver=account,amount=dividend, confirmed_at=timezone.now(),hash=)
                    new_transaction.save()

                    account.balance += dividend
                    account.dividend_due -= dividend
                    account.balance_last_updated = timezone.now()
                    account.save()

                    txn_no.last_txn_no += 1
                    txn_no.save()

'''