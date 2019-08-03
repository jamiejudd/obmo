from django.db import models
from django.utils import timezone
from decimal import Decimal
import core.constants as constants
from django.db.models import Q


#  --------------  STATE  --------------- 
class Account(models.Model): # an account never gets deleted, it costs a txn fee to create an account. i.e. when a new pk get money we create an account.
    public_key = models.CharField(max_length=64, unique=True) #PRIMARYKEY no as longer??  # fixed forever, this will be accid in the recovery setting. 
    balance = models.DecimalField(max_digits = 20, decimal_places = 2, default=0) #IntegerField?
    sequence_next = models.IntegerField(default=1)  #PositiveIntegerField
    registered = models.BooleanField(default=False) #if true then minbalance=beta is in effect

    name = models.CharField(max_length=20, null=True) 
    photo = models.ImageField(upload_to = 'account_photos/', null=True) #can exist before reg=true?
    photo_hash = models.CharField(max_length=128,null=True)

    registered_date = models.DateTimeField(null=True) 
    linked = models.BooleanField(default=False) #iff deg>0
    degree = models.IntegerField(default=0)

    committed = models.BooleanField()
    committed_time = models.DateTimeField(null=True)
    committed_hash = models.CharField(max_length=128,null=True)

    balance_due = models.DecimalField(max_digits = 20, decimal_places = 2, default=0) #IntegerField?
    balance_due_last_updated = models.DateTimeField(default=timezone.now)

    settlement_countdown = models.DateTimeField(null=True)  #not null if market active  
    last_position = models.IntegerField(default=0)
    net_votes = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)

    suspended = models.BooleanField(default=False)
    challenge_degree = models.IntegerField(default=0)

    good = models.BooleanField(default=True)
    #is_verified = models.BooleanField(default=False)

    has_offer = models.BooleanField(default=False)
    offer = models.CharField(max_length=120,null=True)

    def is_good(self):
        if 2*self.net_votes >= self.degree:
            return True
        else:
            return False

    # def zone(self):
    #     if 2*self.net_votes >= self.degree:
    #         return 'Good'
    #     else:
    #         return 'Bad'

    def verified(self):
        if 2*self.net_votes >= self.degree and self.linked == True:
            return True
        else:
            return False

    def verification_score(self):
        if self.degree > 0:
            return int(100*self.net_votes/self.degree)
        else:
            return 0

    def update_balance_due(self,timestamp): #run this any time verified changes , just before
        #if self.verified() == True:
        if self.linked == True and self.good == True:
            elapsed_time = timestamp - self.balance_due_last_updated 
            self.balance_due += Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
            self.balance_due_last_updated = timestamp
        else:
            self.balance_due_last_updated = timestamp
        # return smthin?

    def suspend(self,current_time):
        self.suspended = True
        # self.matched_count = 0
        # self.net_votes = 0
        # self.last_position = 0
        # self.settlement_countdown = None
        self.save()

        overlapping_challenges = Challenge.objects.filter(Q(cancelled = False) & Q( finished = False) & (Q(defendant_1 = self) | Q(defendant_2 = self)))
        for och in overlapping_challenges:
            och.cancel()

        arrows_from = Arrow.objects.filter(source = self, cancelled = False)
        for arrow in arrows_from:
            target = arrow.target
            target.update_balance_due(current_time)
            #old_zone = target.zone()
            old_is_good = target.is_good()
            target.degree -= 1
            target.net_votes -= arrow.status
            target.good = target.is_good()
            if arrow.matched == True:
                target.matched_count -= 1
                matched_arrow = Arrow.objects.filter(target = target, cancelled = False, matched = True, status = -arrow.status).order_by('-position')[0]
                matched_arrow.matched = False
                matched_arrow.save()

            if target.matched_count > 0:
                #if target.zone() != old_zone:
                if target.is_good() != old_is_good:
                    target.settlement_countdown = current_time
            else:
                 target.settlement_countdown = None
            target.save()

            arrow.cancelled = True 
            # arrow.status = 0 
            # arrow.matched = False 
            # arrow.position = None 
            arrow.save()

        arrows_to = Arrow.objects.filter(target = self, cancelled = False)
        for arrow in arrows_from:
            arrow.cancelled = True
            # arrow.status = 0
            # arrow.matched = False
            # arrow.position = None
            arrow.save()


        challengelinks = ChallengeLink.objects.filter(voter = self, cancelled = False)
        for challengelink in challengelinks:
            challenge = challengelink.challenge
            old_is_good = challenge.is_good()
            challenge.degree -= 1
            challenge.net_votes -= challengelink.status
            challenge.good = challenge.is_good()
            if challengelink.matched == True:
                challenge.matched_count -= 1
                matched_challengelink = ChallengeLink.objects.filter(challenge = challenge, cancelled = False, matched = True, status = -challengelink.status).order_by('-position')[0]
                matched_challengelink.matched = False
                matched_challengelink.save()
            challenge.net_votes_who -= challengelink.status_who
            if challengelink.matched_who == True:
                challenge.matched_count_who -= 1
                matched_who_challengelink = ChallengeLink.objects.filter(challenge = challenge, cancelled = False, matched_who = True, status_who = -challengelink.status_who).order_by('-position_who')[0]
                matched_who_challengelink.matched_who = False
                matched_who_challengelink.save()

            if challenge.matched_count > 0:
                if challenge.is_good() != old_is_good:
                    challenge.settlement_countdown = current_time
            else:
                 challenge.settlement_countdown = None
            challenge.save()

            challengelink.cancelled = True
            #challengelink.cancelled = True
            challengelink.save()


class Arrow(models.Model):  #here we use double entry, need to ensure integrity (i.e one arrow exists iff its opposite does)  #never deleted,so we can foreign key to them. created by us, epired by us.   
    source = models.ForeignKey(Account, related_name='outgoing_arrows',on_delete=models.CASCADE)  #no cascade??not relevent as account 'never' gets deleted  #also this never gets deleted
    target = models.ForeignKey(Account, related_name='incoming_arrows',on_delete=models.CASCADE)
    status_choices = ((0, 'Neutral'),(1, 'Trust'),(-1, 'Distrust'))   #change to yes/no?
    status = models.IntegerField(choices=status_choices, default = 0)
    matched = models.BooleanField(default=False)
    position = models.IntegerField(null=True)
    cancelled = models.BooleanField(default=False)
    has_new_message = models.BooleanField(default=False)

    def opposite(self):
        return Arrow.objects.get(source=self.target, target=self.source, cancelled=False) #only works for active arrows

   
class Challenge(models.Model):  #here we need to ensure exclusivity on 12 and 21    
    challenger = models.ForeignKey(Account, related_name = 'challenges_created', on_delete=models.CASCADE)
    defendant_1 = models.ForeignKey(Account, related_name = 'challenges_against_1', on_delete=models.CASCADE)
    defendant_2 = models.ForeignKey(Account, related_name = 'challenges_against_2', on_delete=models.CASCADE)
    created = models.DateTimeField(null=True)
    linked = models.BooleanField(default=False) 
    degree = models.IntegerField(default=0)
    settlement_countdown = models.DateTimeField(null=True) # = None iff matched_count=0

    last_position = models.IntegerField(default=0)
    net_votes = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0) 

    last_position_who = models.IntegerField(default=0)
    net_votes_who = models.IntegerField(default=0)
    matched_count_who = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    good = models.BooleanField(default=True)

    def is_good(self):
        if 2*self.net_votes >= self.degree:
            return True
        else:
            return False

    def verification_score(self):
        if self.linked == True:
            return int(100*self.net_votes/self.degree) 
        else:
            return 0

    def zone(self):
        if 2*self.net_votes >= self.degree:
            return 'Good'
        else:
            return 'Bad'

    def verified(self):
        if 2*self.net_votes >= self.degree and self.linked == True:
            return True
        else:
            return False

    def cancel(self):
        self.cancelled = True
        self.save()
        creation_event = ChallengeCreation.objects.get(challenge=self)
        challenger = self.challenger
        challenger.balance += creation_event.amount
        challenger.save()
        challengelinks = ChallengeLink.objects.filter(challenge = self, cancelled = False, finished = False)
        for challengelink in challengelinks:
            challengelink.cancelled = True
            challengelink.save()

    def finish(self):
        self.finished = True
        self.save()
        challengelinks = ChallengeLink.objects.filter(challenge = self, cancelled = False, finished = False)
        for challengelink in challengelinks:
            challengelink.finished = True
            challengelink.save()

 

class ChallengeLink(models.Model):   
    challenge = models.ForeignKey(Challenge, related_name = 'challengelinks',on_delete=models.CASCADE)
    voter = models.ForeignKey(Account, related_name = 'challengelinks',on_delete=models.CASCADE) #same name should be fine here

    status_choices = ((0, 'Neutral'),(1, 'Trust'),(-1, 'Distrust')) 
    status = models.IntegerField(choices=status_choices, default = 0)
    matched = models.BooleanField(default=False)
    position = models.IntegerField(null=True)

    status_who_choices = ((0, 'Neutral'),(1, 'Account1'),(-1, 'Account2')) 
    status_who = models.IntegerField(choices=status_who_choices, default = 0)
    matched_who = models.BooleanField(default=False)
    position_who = models.IntegerField(null=True)
    finished = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    has_new_message = models.BooleanField(default=False)




class EventCounter(models.Model):  #used for selectforupdate 
    last_event_no = models.IntegerField()


# class Statistic(models.Model): #global output vars
#     supply = models.DecimalField(max_digits = 20, decimal_places = 2)
#     registered = models.IntegerField()
#     num_verified = models.IntegerField()
#     def stake(self):
#         return supply/(2*verified+1)  #min this and 18000
# class Statistics(models.Model): #global output vars
#     name = models.CharField(max_length=10, unique=True)
#     value = models.IntegerField()
# class Parameter(models.Model): #global input vars  #ParameterGroup is a better name
#     beta = models.DecimalField(max_digits = 20, decimal_places = 2)
#     alpha = models.IntegerField()



# --------- TRANSACTIONS ----------- (i.e. ops that change the state) they are only added, never deleted or changed, and certain ones need to be easy to query
class Event(models.Model):
    timestamp = models.DateTimeField()
    event_type_choices = (('Txn','Transaction'),('AC','ArrowCreation'),('AE','ArrowExpiration'),('MS','MarketSettlement'),('MST','MarketSettlementTransfer'),('BU','BalanceUpdate'),('CLC','ChallengeLinkCreation'),('CLE','ChallengeLinkExpiration'),('CS', 'ChallengeSettlement'),('CST', 'ChallengeSettlementTransfer')) 
    event_type = models.CharField(max_length=4, choices = event_type_choices)

# by user
class Txn(models.Model):
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    txn_previous_hash = models.CharField(max_length=128)
    txn_type_choices = (('Transfer','Transfer'),('Commitment','Commitment'),('Revealation','Revealation'),('Register','Register'),('ChangeVote','ChangeVote'),('Challenge','Challenge'),('ChangeChallengeVote','ChangeChallengeVote'))
    txn_type = models.CharField(max_length=20, choices = txn_type_choices)
    sender = models.ForeignKey(Account,on_delete=models.CASCADE) 
    sender_seq_no = models.IntegerField()
    txn_message = models.CharField(max_length=328)
    signature = models.CharField(max_length=128)
    txn_data = models.CharField(max_length=1328)
    txn_hash = models.CharField(max_length=128) #this is hash of txn_data

class Registration(models.Model):
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    name = models.TextField(max_length=30) #text or char?
    photo_hash = models.CharField(max_length=128)

class Transfer(models.Model): 
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    recipient = models.ForeignKey(Account, related_name = 'transfers_recieved',on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits = 20, decimal_places = 2)

class Commitment(models.Model): 
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    committed_hash = models.CharField(max_length=128)  

class Revelation(models.Model): 
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    commitment = models.OneToOneField(Commitment,on_delete=models.CASCADE,related_name='revelation')
    revealed_value = models.CharField(max_length=128)

class ArrowUpdate(models.Model): 
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    arrow = models.ForeignKey(Arrow,on_delete=models.CASCADE)
    arrowupdate_choices = ((0, 'Neutral'),(1, 'Trust'),(-1, 'Distrust'))   #change to yes/no?
    arrowupdate = models.IntegerField(choices=arrowupdate_choices)

class ChallengeCreation(models.Model):
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    challenge = models.OneToOneField(Challenge,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits = 20, decimal_places = 2)

class ChallengeLinkUpdate(models.Model): 
    txn = models.OneToOneField(Txn,on_delete=models.CASCADE)
    challengelink = models.ForeignKey(ChallengeLink, related_name = 'challengelinkupdate_set',on_delete=models.CASCADE)
    challengelinkupdate_choices = ((0, 'Neutral'),(1, 'Trust'),(-1, 'Distrust'))
    challengelinkupdate = models.IntegerField( choices = challengelinkupdate_choices)
    challengelink_who_update_choices = ((0, 'Neutral'),(1, 'Account1'),(-1, 'Account1'))
    challengelink_who_update = models.IntegerField(choices = challengelink_who_update_choices)


# by us
class BalanceUpdate(models.Model):  
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE) 
    amount = models.DecimalField(max_digits = 20, decimal_places = 2, null=True)

class ArrowCreation(models.Model):  
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    arrow = models.OneToOneField(Arrow,on_delete=models.CASCADE)
# class ArrowExpiration(models.Model): 
#     event = models.OneToOneField(Event)
#     arrow = models.OneToOneField(Arrow)

class MarketSettlement(models.Model):  
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE) 
class MarketSettlementTransfer(models.Model):
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    market_settlement = models.ForeignKey(MarketSettlement,on_delete=models.CASCADE) 
    payee = models.ForeignKey(Account,on_delete=models.CASCADE) 
    amount = models.DecimalField(max_digits = 20, decimal_places = 2)

class ChallengeLinkCreation(models.Model):
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    challengelink = models.ForeignKey(ChallengeLink, related_name = '+',on_delete=models.CASCADE)
# class ChallengeLinkExpiration(models.Model):  
#     event = models.OneToOneField(Event)
#     challengelink = models.ForeignKey(ChallengeLink, related_name = '+')

class ChallengeSettlement(models.Model):
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge,on_delete=models.CASCADE) 
class ChallengeSettlementTransfer(models.Model):
    event = models.OneToOneField(Event,on_delete=models.CASCADE)
    challenge_settlement = models.ForeignKey(ChallengeSettlement,on_delete=models.CASCADE) 
    payee = models.ForeignKey(Account,on_delete=models.CASCADE) 
    amount = models.DecimalField(max_digits = 20, decimal_places = 2)


class Message(models.Model):  
    sender = models.ForeignKey(Account,related_name = 'sent_msgs',on_delete=models.CASCADE)
    recipient = models.ForeignKey(Account,related_name = 'received_msgs',on_delete=models.CASCADE)
    content = models.TextField(max_length=100)
    timestamp = models.DateTimeField() 


class MessageCh(models.Model):   #a message belonging to a challenge's chatroom THIS EXTRA MODEL NOT NEEDED?
    sender = models.ForeignKey(Account,on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge,on_delete=models.CASCADE)
    content = models.TextField(max_length=100)
    timestamp = models.DateTimeField() 





#EXTRA
#by user

# class PasswordUpdate(models.Model):  
#     account = models.ForeignKey(Account, on_delete=models.CASCADE) 
#     timestamp = models.DateTimeField() 

#by us

# class ParameterCreation(models.Model): 
#     timestamp = models.DateTimeField() 
#     parameter = models.ForeignKey(Parameter, related_name = 'parametercreation_set')
#     #name = models.CharField(max_length=28)
#     #value = models.DecimalField(max_digits = 20, decimal_places = 2)
# class ParameterUpdate(models.Model): 
#     timestamp = models.DateTimeField() 
#     parameter = models.ForeignKey(Parameter, related_name = 'parameterupdate_set')
#     value = models.DecimalField(max_digits = 20, decimal_places = 2)






 # ~~ TRIGGERED BY USER ~~

# class Txn(models.Model):
#     txn_previous_hash = models.CharField(max_length=128)
#     txn_created = models.DateTimeField(default=timezone.now)
#     txn_type_choices = (('Transfer', 'Transfer'),('Registration', 'Registration'),('ChangeVote', 'ChangeVote'),('Challenge', 'Challenge'),('ChangeChallengeVote', 'ChangeChallengeVote')) #could seperate further here if functionality required it
#     txn_type = models.CharField(max_length=20, choices = txn_type_choices)
#     sender = models.ForeignKey(Account, related_name = 'txns_sent') #unie=tru, 1to1?
#     sender_seq_no = models.IntegerField()
#     signature = models.CharField(max_length=128)
#     txn_hash = models.CharField(max_length=128) #this is hash of txn_data

#     name = models.TextField(max_length=30, null=True) #text or char?
#     photo_hash = models.CharField(max_length=128, null=True)

#     recipient = models.ForeignKey(Account, related_name = 'txns_recieved', null=True)
#     amount = models.DecimalField(max_digits = 20, decimal_places = 2, null=True)

#     vote_choices = (('Neutral', 'Neutral'),('Trust', 'Trust'),('Distrust', 'Distrust'))   #setting to t or d is like making a bet so need bal>minbal
#     vote = models.CharField(max_length=8, choices = vote_choices, null=True)

#     #defendant_1 = models.ForeignKey(Account, related_name = 'challenges_against_1', null=True)
#     #defendant_2 = models.ForeignKey(Account, related_name = 'challenges_against_2', null=True)

#     # challengelink = models.ForeignKey(ChallengeLink, related_name = 'challengelinkupdate_set', null=True)
#     # challengelinkupdate_type_choices = (('N', 'neutral'),('S', 'support'),('O', 'oppose'))
#     # challengelinkupdate_type = models.CharField(max_length=1, choices = challengelinkupdate_type_choices, null=True)
#     txn_message = models.CharField(max_length=328)
#     txn_data = models.CharField(max_length=1328)


# class Message(models.Model):   #a message is a transaction since it doesnt get updated
#     sender = models.ForeignKey(Account,related_name = 'sent_msgs')
#     receiver = models.ForeignKey(Account,related_name = 'received_msgs')
#     content = models.TextField(max_length=100)
#     timestamp = models.DateTimeField(null=True) 
# class MessageCh(models.Model):   #a message belonging to a challenge's chatroom THIS EXTRA MODEL NOT NEEDED?
#     sender = models.ForeignKey(Account,related_name = 'sent_msgs')
#     receiver = models.ForeignKey(Account,related_name = 'received_msgs')
#     content = models.TextField(max_length=100)
#     timestamp = models.DateTimeField(null=True) 

# class PasswordUpdate(models.Model):  
#     account = models.ForeignKey(Account, on_delete=models.CASCADE) 
#     timestamp = models.DateTimeField() 


 # ~~ TRIGGERED BY US ~~
# class AccountCreation(models.Model):  #rarely used
#     timestamp = models.DateTimeField() 
#     account = models.ForeignKey(Account, related_name = '+')


# class DividendTransfer(models.Model):  
#     account = models.ForeignKey(Account, on_delete=models.CASCADE) 
#     timestamp = models.DateTimeField() 
#     amount = models.DecimalField(max_digits = 20, decimal_places = 2, null=True)


# class ArrowCreation(models.Model):  
#     timestamp = models.DateTimeField() 
#     arrow = models.ForeignKey(Arrow, related_name = 'arrowcreation_set') #unique=true, 121  #related name?
# class ArrowExpiration(models.Model): 
#     timestamp = models.DateTimeField() 
#     arrow = models.ForeignKey(Arrow, related_name = 'arrowexpiration_set') #unique=true, 121  #related name?


# class MarketSettlement(models.Model):  
#     account = models.ForeignKey(Account) 
#     timestamp = models.DateTimeField() 
# class MarketSettlementTransfer(models.Model):
#     market_settlement = models.ForeignKey(MarketSettlement) 
#     payee = models.ForeignKey(Account) 
#     amount = models.DecimalField(max_digits = 20, decimal_places = 2)



# class ChallengeLinkCreation(models.Model): 
#     timestamp = models.DateTimeField() 
#     challengelink = models.ForeignKey(ChallengeLink, related_name = '+') #unique=true, 121  #related name?
# class ChallengeLinkExpiration(models.Model):  
#     timestamp = models.DateTimeField() 
#     challengelink = models.ForeignKey(ChallengeLink, related_name = '+') #unique=true, 121  #related name?



# class ChallengeSettlement(models.Model): 
#     challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE) 
#     timestamp = models.DateTimeField() 
# class ChallengeSettlementTransfer(models.Model): 
#     challenge_settlement = models.ForeignKey(ChallengeSettlement) 
#     payee = models.ForeignKey(Account) 
#     amount = models.DecimalField(max_digits = 20, decimal_places = 2)





# class ParameterCreation(models.Model): 
#     timestamp = models.DateTimeField() 
#     parameter = models.ForeignKey(Parameter, related_name = 'parametercreation_set')
#     #name = models.CharField(max_length=28)
#     #value = models.DecimalField(max_digits = 20, decimal_places = 2)
# class ParameterUpdate(models.Model): 
#     timestamp = models.DateTimeField() 
#     parameter = models.ForeignKey(Parameter, related_name = 'parameterupdate_set')
#     value = models.DecimalField(max_digits = 20, decimal_places = 2)







'''
+schema
-----STATE-----
ACCOUNT  [OBJ]
CHALLENGE [OBJ]
ARROW (ACC->ACC)  [MOR]
CHALLENGELINK (ACC->CHALL)   [MOR]
PARAMETER 

-----TRANSACTIONS-----
BY USER:    UPDATE ACCOUNT         register (requires balance>minbal) #OC  
            UPDATE ACCOUNT         update password     
            UPDATE ACCOUNT         transfer  ~OC                           
            UPDATE ARROW           ~OC                   
            CREATE CHALLENGE       def1,def2  ~OC                
            UPDATE CHALLENGELINK   neutral/supp/oppose  ~OC

BY US:      CREATE ACCOUNT
            CREATE ARROW                changes in ARROW also updates account.verified?
            UPDATE ARROW                make arrow expired
            UPDATE ACCOUNT              update balance from ubi
            UPDATE ACCOUNTS+ARROWS      settle market
            CREATE CHALLENGELINK
            UPDATE CHALLENGELINK        make challengelink expired
            UPDATE CHALLENGE+ACCOUNTS   settle challenge, make the challenge expired, adjust balances, 
            UPDATE PARAMETER
            CREATE PARAMETER
'''






'''
class AccountAction(models.Model): 
    account = models.ForeignKey(Account, related_name = 'accountaction_set') 
    timestamp = models.DateTimeField()
    accountaction_type_choices = (('C', 'creation'),('B', 'balanceupdate'),('S', 'settlement'))
    accountaction_type = models.CharField(max_length=1, choices = account_action_type_choices) 

class ArrowAction(models.Model): 
    arrow = models.ForeignKey(Arrow, related_name = 'arrowaction_set') #unique=true, 121  #related name?
    timestamp = models.DateTimeField()
    arrowaction_type_choices = (('C', 'creation'),('E', 'expiration'))
    arrowaction_type = models.CharField(max_length=1, choices = arrowaction_type_choices)

class ChallengeLinkAction(models.Model): 
    challengelink = models.ForeignKey(Challenge, related_name = '+') #unique=true, 121  #related name?
    timestamp = models.DateTimeField()
    challengelinkaction_type_choices = (('C', 'creation'),('E', 'expiration'))
    challengelinkaction_type = models.CharField(max_length=1, choices = challengelinkaction_type_choices)

class ChallengeAction(models.Model): 
    challenge = models.ForeignKey(ChallengeLink, related_name = '+') #unique=true, 121  #related name?
    timestamp = models.DateTimeField()
    challengelinkaction_type_choices = (('S', 'settlement'))
    challengelinkaction_type = models.CharField(max_length=1, choices = challengelinkaction_type_choices)
'''





    




    #sender = models.CharField(max_length=64, null=True)
    #sender_seq_no = models.IntegerField(null=True)
    #recipient1 = models.CharField(max_length=64,null=True)
    #recipient2 = models.ForeignKey(Account,related_name = 'recieved_txns_2',null=True)
    #challenge = models.ForeignKey(Challenge,related_name = 'challenge_votes',null=True)
    #amount = models.DecimalField(max_digits = 20, decimal_places = 2, null=True)
    #signature = models.CharField(max_length=128, null=True)
    #name = models.TextField(max_length=30) #text or char?
    #txn_photo = models.ImageField(upload_to = 'txn_photos/',null=True)
    #txn_photo_hash = models.CharField(max_length=128)


'''
    #maximum_seq_number = models.IntegerField(default = 1)


    applicant = models.ForeignKey(Account,related_name = 'applications')
    name = models.TextField(max_length=30) #text or char?
    txn_photo = models.ImageField(upload_to = 'txn_photos/', default = 'pic_folder/None/no-img.jpg')
    txn_photo_hash = models.CharField(max_length=30)

    link1 = models.ForeignKey(Account,related_name = 'link1_txns')
    link2 = models.ForeignKey(Account,related_name = 'link2_txns')

    voucher = models.ForeignKey(Account,related_name = 'vouches_given')
    vouchee = models.ForeignKey(Account,related_name = 'vouches_recieved')

    distruster = models.ForeignKey(Account,related_name = 'distrusts_given')
    distrustee = models.ForeignKey(Account,related_name = 'distrusts_recieved')

    challenger = models.ForeignKey(Account,related_name = 'challenge_txns_created')
    challengee1 = models.ForeignKey(Account,related_name = 'challenge1_txns_against')
    challengee2 = models.ForeignKey(Account,related_name = 'challenge2_txns_against')
'''

    

'''
#for account:
    how best to structure these bits? theyre basically separate tables of links, trusts,etc..
    links = models.ManyToManyField('self') #related name = links_set
    trusts = models.ManyToManyField('self', related_name='trusted_by', symmetrical=False) 
    distrusts = models.ManyToManyField('self', related_name='distrusted_by', symmetrical=False) 

    def make_verified(self):
        if (self.verified == false):
            self.verified = true
            self.last_checkpoint = timezone.now()
        else:
            raise ValueError("already verified")

    def make_unverified(self):
        if (self.verified == true):
            self.verified = false
            if (timezone.now()-self.last_checkpoint > 0.01):
                self.dividend_due += (timezone.now()-self.last_checkpoint)*0.023
            self.last_checkpoint = timezone.now()
        else:
            raise ValueError("already unverified")
'''

'''
#here we have to make complex queries, ie. depending on if accc is acc1 or acc2. ALso, may want to have a key to messages
class Link(models.Model): 
    account1 = models.ForeignKey(Account, related_name='links1', on_delete=models.CASCADE)  #no cascade?? not relevent as account 'never' gets deleted
    account2 = models.ForeignKey(Account, related_name='links2', on_delete=models.CASCADE)
    status_choices = (('N', 'neutral'),('T', 'trust'),('D', 'distrust')) 
    status1 = models.CharField(max_length=1, choices = status_choices)
    status2 = models.CharField(max_length=1, choices = status_choices)
    matched1 = models.BooleanField(default=False)
    matched2 = models.BooleanField(default=False)
'''

#-- this is for account recovery feature, not part of mvp --
#account_id = models.CharField(max_length=30) #unique
#public_key = models.CharField(max_length=30) #not necc unique, ie one sk can control two accounts
#recovery_pks = ArrayField(models.CharField(max_length=200), blank=True) # need array instead of foreign key, as recovery pks may not be accounts.
#number_needed = models.IntegerField(default=0)
#time_lag_hours = models.IntegerField(default=0)




'''
class PhotoUpdate(models.Model):  
    account = models.ForeignKey(Account, related_name = 'photoupdate_set') 
    photo = models.ImageField(upload_to = 'photoupdates/')
    photo_hash = models.CharField(max_length=128)
'''