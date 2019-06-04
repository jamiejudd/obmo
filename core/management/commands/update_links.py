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
        #be sure to update verified when ever votes or degree changes, i.e keep veified up to date
        #this code always needs to be run just before we update verified (just the version for a single account tho)

        #UPDATE LINKS
        cutoff_time = timezone.now() - timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)

        #while still someone left to add:
        account = Account.objects.filter(linked=False,registered=True,registered_date__lte=cutoff_time).order_by('registered_date').first()
        t2 = account.registered_date
        t1 = t2 - timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)

        commits = Commitment.objects.select_related('revelation').filter(txn__event__timestamp__gte=t1,txn__event__timestamp__lte=t2)
        
        commits = Commitment.objects.select_related('revelation').filter(Q(Q(txn__event__timestamp__gte=t1) & Q(txn__event__timestamp__lte=t2)))

Recipe.objects.filter(Q(Q(ingredient_set__id=1, ingredient_set__amount__lte=10) | Q(ingredient_set__id=2, ingredient_set__amount__lte=15)))



        for x in Account.objects.values_list('id',flat=True):
            with transaction.atomic():
                account = Account.objects.select_for_update().get(id=x)
                current_time = timezone.now()
                if (account.verified == True):
                    elapsed_time = current_time - account.balance_due_last_updated 
                    elapsed_time_seconds = Decimal(elapsed_time.total_seconds())
                    dividend = elapsed_time_seconds*Decimal(0.0011574074)  # 100/24*3600=0.0011574074
                    account.balance_due += dividend
                    #account.total_ubi_generated += dividend
                    account.balance_due_last_updated = current_time
                    account.save()
                else:
                    account.balance_due_last_updated = current_time
                    account.save()
              

