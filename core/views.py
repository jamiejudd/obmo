from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404


from core.models import Account, Arrow, Challenge, ChallengeLink, EventCounter, Message, MessageCh
from core.models import Event, Txn, Registration, Transfer, Commitment, Revelation, ArrowUpdate, ChallengeCreation, ChallengeLinkUpdate
from core.models import BalanceUpdate, ArrowCreation, ChallengeLinkCreation, MarketSettlement, MarketSettlementTransfer
from core.models import Message

from core.forms import  RegisterForm,TransferForm,UserRegistrationForm,ResetPasswordForm,CommitForm,RevealForm
from core.forms import  ArrowUpdateForm,ChallengeForm,ChallengeLinkUpdateForm, OfferForm
import core.constants as constants

from django.db.models import Q
from django.db.models import Sum


from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


from django.contrib import messages
#from django.contrib.messages import get_messages

from django.utils import timezone

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii

from decimal import Decimal

from django.http import JsonResponse

#GETS
def index(request):
    return render(request, 'core/index.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def accounts(request):
    accounts_all = Account.objects.order_by('suspended','-registered','-id')
    # try:
    #     per_page = int(request.REQUEST['count'])
    # except:
    #     per_page = 1     # default value
    paginator = Paginator(accounts_all,20) # Show 25 contacts per page, too many -> loads slowly
    page = request.GET.get('page')
    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        accounts = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/accounts.html', {'accounts':accounts})

def account(request,username):
    try:
        account = Account.objects.get(public_key=username)
    except Account.DoesNotExist:
        raise Http404("Account does not exist")
    arrows = Arrow.objects.filter(target=account)
    challengelinks = ChallengeLink.objects.filter(voter=account,finished=False,cancelled=False)
    challenges_by = Challenge.objects.filter(challenger=account,finished=False,cancelled=False)
    challenges_against = Challenge.objects.filter(Q(defendant_1=account) | Q(defendant_2=account),finished=False,cancelled=False)

    countdown = None
    total_seconds = None
    if account.settlement_countdown is not None:
        td = account.settlement_countdown + timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME) - timezone.now()
        countdown = format_timedelta(td)
        total_seconds = td.total_seconds()
    return render(request, 'core/account.html',{'username':username,'account':account,'arrows':arrows,'challengelinks':challengelinks,'challenges_by':challenges_by,'challenges_against':challenges_against,'countdown':countdown,'total_seconds':total_seconds})

def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return '{:2}d {:2}h {:2}m {:2}s'.format(int(days),int(hours), int(minutes), int(seconds))

@login_required 
def myaccount(request):
    account = Account.objects.get(public_key=request.user.username)
    arrows = Arrow.objects.filter(target=account).order_by('id')
    challengelinks = ChallengeLink.objects.filter(voter=account,finished=False,cancelled=False)
    challenges_by = Challenge.objects.filter(challenger=account,finished=False,cancelled=False)
    challenges_against = Challenge.objects.filter(Q(defendant_1=account) | Q(defendant_2=account),finished=False,cancelled=False)

    msgs = Message.objects.filter(Q(sender=account) | Q(recipient=account))
    linked_challenges = [challengelink.challenge for challengelink in challengelinks]
    msgs_ch = MessageCh.objects.filter(challenge__in = linked_challenges)
    
    if len(arrows) > 0:
        first_arrow = arrows[0]
        first_arrow.has_new_message = False
        first_arrow.save()

    offer = None
    if account.has_offer == True:
        offer = account.offer

    countdown = None
    total_seconds = None
    if account.settlement_countdown is not None:
        td = account.settlement_countdown + timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME) - timezone.now()
        countdown = format_timedelta(td)
        total_seconds = td.total_seconds()

    time_status = None
    timer = None
    if account.committed:
        td = timezone.now() - account.committed_time
        td1 = timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)
        td2 = timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
        if td < td1:
            time_status = 'early'
            #timer = format_timedelta(td1 - td)
            timer = str(td1 - td).split(".")[0]
        elif td < td2:
            time_status = 'ready'
            timer = str(td2 - td).split(".")[0]
        else:
            time_status = 'late'
            timer = str(td - td2).split(".")[0]
    return render(request, 'core/myaccount.html',{'username':request.user.username,'account':account,'arrows':arrows,'challengelinks':challengelinks,'challenges_by':challenges_by,'challenges_against':challenges_against,'countdown':countdown,'total_seconds':total_seconds,'time_status':time_status,'timer':timer,'offer':offer,'msgs':msgs,'msgs_ch':msgs_ch})

def account_history(request,username):
    try:
        account = Account.objects.get(public_key=username)
    except Account.DoesNotExist:
        raise Http404("Account does not exist")
    events_all = Event.objects.prefetch_related('txn','txn__transfer','txn__registration','txn__commitment','txn__revelation','txn__arrowupdate','txn__challengecreation','txn__challengelinkupdate','arrowcreation','challengelinkcreation','marketsettlement','marketsettlementtransfer','challengesettlementtransfer').filter(Q(txn__sender=account) | Q(txn__transfer__recipient=account) | Q(txn__arrowupdate__arrow__target=account) | Q(txn__challengecreation__challenge__defendant_1=account)  | Q(txn__challengecreation__challenge__defendant_2=account)| Q(balanceupdate__account=account)| Q(arrowcreation__arrow__source=account) | Q(challengelinkcreation__challengelink__voter=account)| Q(marketsettlement__account=account)| Q(marketsettlementtransfer__payee=account)| Q(challengelinkcreation__challengelink__voter=account)| Q(challengesettlementtransfer__payee=account)).order_by('-id')
    paginator = Paginator(events_all, 50) 
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        events = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/account_history.html',{'username':username,'events':events})    


@login_required 
def myaccount_history(request):
    account = Account.objects.get(public_key=request.user.username)
    events_all = Event.objects.prefetch_related('txn','txn__transfer','txn__registration','txn__commitment','txn__revelation','txn__arrowupdate','txn__challengecreation','txn__challengelinkupdate','arrowcreation','challengelinkcreation','marketsettlement','marketsettlementtransfer','challengesettlementtransfer').filter(Q(txn__sender=account) | Q(txn__transfer__recipient=account) | Q(txn__arrowupdate__arrow__target=account) | Q(txn__challengecreation__challenge__defendant_1=account)  | Q(txn__challengecreation__challenge__defendant_2=account)| Q(balanceupdate__account=account)| Q(arrowcreation__arrow__source=account) | Q(challengelinkcreation__challengelink__voter=account)| Q(marketsettlement__account=account)| Q(marketsettlementtransfer__payee=account)| Q(challengelinkcreation__challengelink__voter=account)| Q(challengesettlementtransfer__payee=account)).order_by('-id')
    paginator = Paginator(events_all, 50) 
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        events = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/account_history.html',{'username':request.user.username,'events':events})    


def txns(request):
    txns_all = Txn.objects.all().select_related('event').order_by('-id')
    paginator = Paginator(txns_all, 100) # Show 25 contacts per page, too many -> loads slowly
    page = request.GET.get('page')
    try:
        txns = paginator.page(page)
    except PageNotAnInteger:
        txns = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        txns = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/txns.html',{'txns':txns})

def txn(request,txno):
    txn = Txn.objects.get(id=txno)
    return render(request, 'core/txn.html',{'txno':txno,'txn':txn})

def challenges(request):
    challenges_all = Challenge.objects.all().order_by('-id')
    paginator = Paginator(challenges_all, 15) # Show 25 contacts per page, too many -> loads slowly
    page = request.GET.get('page')
    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        challenges = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        challenges = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/challenges.html', {'challenges':challenges})

def single_challenge(request,challengeid):
    try:
        challenge = Challenge.objects.get(id=challengeid)
    except Challenge.DoesNotExist:
        raise Http404("Challenge does not exist")
    challengelinks = ChallengeLink.objects.filter(challenge=challenge,finished=False,cancelled=False)
    countdown = None
    total_seconds = None
    if challenge.settlement_countdown is not None:
        td = challenge.settlement_countdown + timezone.timedelta(seconds=constants.CHALLENGE_SETTLEMENT_TIME) - timezone.now()
        countdown = format_timedelta(td)
        total_seconds = td.total_seconds()
    return render(request, 'core/single_challenge.html',{'challengeid':challengeid,'challenge':challenge,'challengelinks':challengelinks,'countdown':countdown,'total_seconds':total_seconds})

def single_challenge_history(request,challengeid):
    try:
        challenge = Challenge.objects.get(id=challengeid)
    except Challenge.DoesNotExist:
        raise Http404("Challenge does not exist")
    events_all = Event.objects.prefetch_related('txn','txn__challengecreation','txn__challengelinkupdate','challengelinkcreation','challengesettlement','challengesettlementtransfer').filter( Q(txn__challengecreation__challenge=challenge)| Q(txn__challengelinkupdate__challengelink__challenge=challenge)| Q(challengelinkcreation__challengelink__challenge=challenge)| Q(challengesettlement__challenge=challenge)| Q(challengesettlementtransfer__challenge_settlement__challenge=challenge)).order_by('-id')
    paginator = Paginator(events_all, 50) 
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        events = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/single_challenge_history.html',{'challengeid':challengeid,'events':events})    

def exchange2(request):
    #return render(request, 'core/transactions.html')
    accounts = Account.objects.all().order_by('id')
    arrows = Arrow.objects.all()
    challenges = Challenge.objects.all()
    challengelinks = ChallengeLink.objects.all()
    event_counters = EventCounter.objects.all()
    events = Event.objects.all()
    txns = Txn.objects.all()
    registrations = Registration.objects.all()
    transfers = Transfer.objects.all()
    arrow_updates = ArrowUpdate.objects.all()
    balance_updates = BalanceUpdate.objects.all()
    MarketSettlementTransfers = MarketSettlementTransfer.objects.all()
    MarketSettlements = MarketSettlement.objects.all()
    commitments = Commitment.objects.all()
    revelations = Revelation.objects.all()
    return render(request, 'core/exchange2.html',{'accounts':accounts,'arrows':arrows,'challenges':challenges,'challengelinks':challengelinks,'commitments':commitments,'revelations':revelations,'event_counters':event_counters,'events':events,'txns':txns,'registrations':registrations,'transfers':transfers,'arrow_updates':arrow_updates,'balance_updates':balance_updates,'MarketSettlementTransfers':MarketSettlementTransfers,'MarketSettlements':MarketSettlements})
    #return render(request, 'core/index2.html')
    
def exchange(request):
    accounts_with_offers = Account.objects.filter(suspended=False,registered=True,has_offer=True)
    return render(request, 'core/exchange.html',{'accounts_with_offers':accounts_with_offers})
    
def statistics(request):
    supply = Account.objects.aggregate(Sum('balance'))['balance__sum']
    num_registered = Account.objects.filter(registered=True).count()
    num_verified = Account.objects.filter(suspended=False,linked=True,good=True).count()
    min_balance = constants.MIN_BALANCE
    bet_bad = constants.BET_BAD
    bet_good = constants.BET_GOOD
    market_settlement_time = constants.MARKET_SETTLEMENT_TIME
    challenger_bet = constants.CHALLENGER_BET
    challenger_reward = constants.CHALLENGER_REWARD
    challenge_bet_good = constants.CHALLENGE_BET_GOOD
    challenge_bet_bad = constants.CHALLENGE_BET_BAD
    challenge_bet_who = constants.CHALLENGE_BET_WHO
    challenge_settlement_time = constants.CHALLENGE_SETTLEMENT_TIME
    num_links = constants.NUM_LINKS
    link_weighting_parameter = constants.LINK_WEIGHTING_PARAMETER
    num_challenge_links = constants.NUM_CHALLENGE_LINKS
    challenge_link_weighting_parameter = constants.CHALLENGE_LINK_WEIGHTING_PARAMETER
    timedelta_1_hours = constants.TIMEDELTA_1_HOURS
    timedelta_2_hours = constants.TIMEDELTA_2_HOURS

    return render(request, 'core/statistics.html',{'supply':supply,'num_registered':num_registered,'num_verified':num_verified,'min_balance':min_balance,'bet_good':bet_good,'bet_bad':bet_bad,'market_settlement_time':market_settlement_time,'challenger_bet':challenger_bet,'challenger_reward':challenger_reward,'challenge_bet_good':challenge_bet_good,'challenge_bet_bad':challenge_bet_bad,'challenge_bet_who':challenge_bet_who,'challenge_settlement_time':challenge_settlement_time,'num_links':num_links,'link_weighting_parameter':link_weighting_parameter,'num_challenge_links':num_challenge_links,'challenge_link_weighting_parameter':challenge_link_weighting_parameter,'timedelta_1_hours':timedelta_1_hours,'timedelta_2_hours':timedelta_2_hours})
    

   
def newkeypair(request):
    return render(request, 'core/newkeypair.html')

def retrievepubkey(request):
    return render(request, 'core/retrievepubkey.html')

def faq(request):
    return render(request, 'core/faq.html', {'min_balance':constants.MIN_BALANCE,'timedelta_2_hours':constants.TIMEDELTA_2_HOURS})

#POSTS
def resetpassword(request):
    if request.method == 'POST':
        print(request.POST)
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data.get('username') 
            new_password = form.cleaned_data.get('new_password') 
            signature = form.cleaned_data.get('signature')

            try:
                account = Account.objects.get(public_key = public_key)
            except Account.DoesNotExist:
                messages.error(request, 'Password reset was unsuccessful. No such account exists.')
                return redirect('/resetpassword/')
   
            u = User.objects.get(username__exact=public_key)
            u.set_password(new_password)
            u.save()
            messages.success(request, 'Password reset was successful.')
            return redirect('/resetpassword/')
        else:
            messages.error(request, 'Password reset was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            return redirect('/resetpassword/') 
    else:
        return render(request, 'core/resetpassword.html')

@login_required 
def offer(request):
    if request.method == 'POST':
        print(request.POST)
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.cleaned_data.get('offer') 
            account = Account.objects.get(public_key = request.user.username)
            if account.has_offer == True:
                #messages.error(request, 'You already has an active offer. Delete that offer first.')
                return redirect('/myaccount/')
            account.has_offer = True
            account.offer = offer
            account.save()
            #messages.success(request, 'Created offer successfully.')
            return redirect('/myaccount/')
        else:
            messages.error(request, 'Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            return redirect('/myaccount/') 
    else:
        return redirect('/myaccount/')


@login_required 
def offer_delete(request):
    if request.method == 'POST':
        account = Account.objects.get(public_key = request.user.username)
        account.has_offer = False
        account.offer = None
        account.save()
        return redirect('/myaccount/')
    else:
        return redirect('/myaccount/')

@login_required 
def mark_read(request):
    if request.method == 'POST':
        target = request.POST.get('target', None) 
        is_ch = request.POST.get('is_ch', None) 
        account = Account.objects.get(public_key = request.user.username)
        if is_ch == 'true':
            target_challenge = Challenge.objects.filter(id = target).first()
            if account is not None and target_challenge is not None:
                challengelink = ChallengeLink.objects.filter(voter=account,challenge=target_challenge).first()
                if challengelink is not None:
                    challengelink.has_new_message = False
                    challengelink.save()
        else:
            target_account = Account.objects.filter(public_key = target).first()
            if account is not None and target_account is not None:
                arrow = Arrow.objects.filter(target=account,source=target_account).first()
                if arrow is not None:
                    arrow.has_new_message = False
                    arrow.save()    #POTENILALLLY BAD?
        return redirect('/myaccount/')
    else:
        return redirect('/myaccount/')

def commit(request):
    if request.method == 'POST':
        form = CommitForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            committed_hash = form.cleaned_data.get('committed_hash') 
            signature = form.cleaned_data.get('signature')
   
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().get(pk=1)
                current_time = timezone.now()
                try:
                    sender = Account.objects.select_for_update().get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/commit/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/commit/')
                if sender.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. You need to be registered to submit random numbers.')
                    return redirect('/commit/')
                if sender.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. This account is suspended.')
                    return redirect('/commit/')
                if sender.committed == True:
                    messages.error(request, 'Transaction was unsuccessful. Already have a commited value. Reveal first.')
                    return redirect('/commit/')

                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                message_string = 'Type:Commit,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Hash:'+committed_hash                       
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)

                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='Commitment',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_commitment = Commitment.objects.create(txn=new_txn,committed_hash=committed_hash)

                sender.committed = True
                sender.committed_time = current_time
                sender.committed_hash = committed_hash
                sender.sequence_next += 1
                sender.save()
                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/commit/')
        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/commit/') 
            return render(request, 'core/commit.html',{'form_errors':form.errors})
    else:
        #form = CommitForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/commit.html',{'account':account,'timedelta_1_hours':constants.TIMEDELTA_1_HOURS})
        else:
            return render(request, 'core/commit.html',{'timedelta_1_hours':constants.TIMEDELTA_1_HOURS})
            #return render(request, 'core/commit.html',{'form':form})


def reveal(request):
    if request.method == 'POST':
        form = RevealForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            revealed_value = form.cleaned_data.get('revealed_value') 
            signature = form.cleaned_data.get('signature')

            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().get(pk=1)
                current_time = timezone.now()
                try:
                    sender = Account.objects.select_for_update().get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/reveal/')
                except:
                    raise Exception('UNKNOWN ERROR22!')

                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/reveal/')
                if sender.committed == False:
                    messages.error(request, 'Transaction was unsuccessful. First you need to commited a value.')
                    return redirect('/reveal/')
                if sender.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. This account is suspended.')
                    return redirect('/reveal/')

                revealed_value_bytes = bytes.fromhex(revealed_value)
                hash_value = nacl.hash.sha512(revealed_value_bytes, encoder=nacl.encoding.RawEncoder)
     
                if sender.committed_hash != hash_value.hex():
                    messages.error(request, 'Transaction was unsuccessful. Incorrect value for hash.')
                    return redirect('/reveal/')

                if current_time < sender.committed_time + timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS) :
                    messages.error(request, 'Transaction was unsuccessful. Reveal too soon.')
                    return redirect('/reveal/')
                
                if current_time > sender.committed_time + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS) :
                    messages.error(request, 'Transaction was unsuccessful. Reveal too late.')
                    return redirect('/reveal/')

                try:
                    commitment = Commitment.objects.filter(txn__sender = sender).last()
                except Commitment.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Serious problem, couldnt find commitment.')
                    return redirect('/reveal/')

                assert commitment.committed_hash == sender.committed_hash

                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                message_string = 'Type:Reveal,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Value:'+revealed_value                       
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)

                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='Revelation',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_revelation = Revelation.objects.create(txn=new_txn,commitment=commitment,revealed_value=revealed_value)

                sender.committed = False
                sender.sequence_next += 1
                sender.save()

                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/reveal/')
        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/reveal/') 
            return render(request, 'core/reveal.html',{'form_errors':form.errors})
    else:
        #form = RevealForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            time_status = None
            timer = None
            if account.committed:
                td = timezone.now() - account.committed_time
                td1 = timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS)
                td2 = timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)
                if td < td1:
                    time_status = 'early'
                    #timer = format_timedelta(td1 - td)
                    timer = str(td1 - td).split(".")[0]
                elif td < td2:
                    time_status = 'ready'
                    timer = str(td2 - td).split(".")[0]
                else:
                    time_status = 'late'
                    timer = str(td - td2).split(".")[0]
            return render(request, 'core/reveal.html',{'account':account,'time_status':time_status,'timer':timer})
        else:
            return render(request, 'core/reveal.html')
            #return render(request, 'core/reveal.html',{'form':form})


def transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            recipient_pk = form.cleaned_data.get('recipient_pk') 
            amount = form.cleaned_data.get('amount') 
            signature = form.cleaned_data.get('signature')

            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                current_time = timezone.now()
                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/transfer/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/transfer/')
                if sender.balance < amount:
                    messages.error(request, 'Transaction was unsuccessful. Insufficient balance')
                    return redirect('/transfer/')
                if sender.registered and sender.balance < constants.MIN_BALANCE + amount:
                    messages.error(request, 'Transaction was unsuccessful. Registered accounts must have a minimum balance of {}'.format(constants.MIN_BALANCE))
                    return redirect('/transfer/')                
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                message_string = 'Type:Transfer,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Recipient:'+recipient_pk+',Amount:'+str(amount)                         
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                try:
                    recipient = Account.objects.get(public_key = recipient_pk)
                except Account.DoesNotExist:
                    recipient = Account.objects.create(public_key = recipient_pk,balance_due_last_updated = current_time, committed=False)

                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='Transfer',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_transfer = Transfer.objects.create(txn=new_txn,recipient=recipient,amount=amount)

                sender.balance -= amount
                recipient.balance += amount
                sender.sequence_next += 1
                sender.save()
                recipient.save()

                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/transfer/')
        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/transfer/') 
            return render(request, 'core/transfer.html',{'form_errors':form.errors})
    else:
        #form = TransferForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/transfer.html',{'account':account})
        else:
            return render(request, 'core/transfer.html')
            #return render(request, 'core/transfer.html',{'form':form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST,request.FILES)
        userform = UserRegistrationForm(request.POST)
        if userform.is_valid() and form.is_valid():
            username = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            name = form.cleaned_data.get('name') 
            #scan img upload with antivirus, at the end save it with standardized file name
            photo = form.cleaned_data.get('photo') 
            photo_hash = form.cleaned_data.get('photo_hash') 
            signature = form.cleaned_data.get('signature')

            if Account.objects.count() == 0:
                with transaction.atomic():
                    event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                    current_time = timezone.now()
                    sender = Account.objects.create(public_key=username,balance=0,balance_due_last_updated = current_time, committed = False)
                    message_string = 'Type:Register,PublicKey:'+username+',SeqNo:1,Name:'+name+',PhotoHash:'+photo_hash
                    txn_data = '"TxnNo":"1","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"Genesis"'
                    txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                    new_event = Event.objects.create(id=1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                    new_txn = Txn.objects.create(id=1,event=new_event,txn_previous_hash='Genesis',txn_type='Register',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                    new_registration = Registration.objects.create(txn=new_txn,name=name,photo_hash=photo_hash)
                    sender.name = name
                    sender.photo = photo
                    sender.photo_hash = photo_hash
                    sender.registered = True
                    sender.registered_date = current_time
                    sender.linked = True
                    sender.verified = True
                    sender.sequence_next += 1
                    userform.save()
                    sender.save()
                    event_counter.last_event_no += 1
                    event_counter.save()
            else:
                with transaction.atomic():
                    event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                    current_time = timezone.now()
                    assert current_time > Event.objects.last().timestamp # cant fail
                    try:
                        sender = Account.objects.get(public_key = username)
                    except Account.DoesNotExist:
                        messages.error(request, 'Transaction was unsuccessful. That account does not exist.') # but this is ok if minbal=0!!
                        return redirect('/register/')
                    if sender.sequence_next != sender_seq_no:
                        messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                        return redirect('/register/') 
                    if sender.registered == True:
                        messages.error(request, 'Transaction was unsuccessful. That account is already registered.')
                        return redirect('/register/')
                    if sender.balance < constants.MIN_BALANCE: #txnfees?
                        messages.error(request, 'Transaction was unsuccessful. Account balance is less that the required minimum.')
                        return redirect('/register/')
                              
                    last_txn = Txn.objects.last()
                    txn_number = last_txn.id+1

                    assert current_time > last_txn.event.timestamp

                    message_string = 'Type:Register,PublicKey:'+username+',SeqNo:'+str(sender_seq_no)+',Name:'+name+',PhotoHash:'+photo_hash
                    txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                    txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)

                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                    new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='Register',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                    new_registration = Registration.objects.create(txn=new_txn,name=name,photo_hash=photo_hash)

                    sender.name = name
                    sender.photo = photo
                    sender.photo_hash = photo_hash
                    sender.registered = True
                    sender.registered_date = current_time
                    sender.sequence_next += 1
                    userform.save()
                    sender.save()
                    event_counter.last_event_no += 1
                    event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/register/')

        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #print('userform.errors')
            #print(userform.errors)
            #print(request.POST['username'])
            return render(request, 'core/register.html',{'form_errors':form.errors})
            #return redirect('/register/') 
    else:
        return render(request, 'core/register.html')


def arrowupdate(request):
    if request.method == 'POST':
        form = ArrowUpdateForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            target_pk = form.cleaned_data.get('target_pk') 
            arrow_status = form.cleaned_data.get('arrow_status') 
            signature = form.cleaned_data.get('signature')

            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                current_time = timezone.now()
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                assert current_time > last_txn.event.timestamp
                    
                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/changevote/')
                
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/changevote/')

                if sender.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. The sender account is suspended.')
                    return redirect('/changevote/')

                if sender.balance < constants.MIN_BALANCE: 
                    messages.error(request, 'Transaction was unsuccessful. Account balance is less that the required minimum.')
                    return redirect('/changevote/')

                try:
                    target = Account.objects.get(public_key = target_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such target account exists.')
                    return redirect('/changevote/')        

                try:
                    arrow = Arrow.objects.get(source = sender, target = target, cancelled = False)
                except Arrow.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such active Arrow exists.')
                    return redirect('/changevote/')        

                if arrow.matched == True:
                    messages.error(request, 'Transaction was unsuccessful. You cannot change your vote/bet as it has already been matched.')
                    return redirect('/changevote/')

                new_status = 1 if arrow_status == 'Trust' else -1 if arrow_status == 'Distrust' else 0 if arrow_status == 'Neutral' else 9

                if arrow.status == new_status:
                    messages.error(request, 'Nothing changed as your vote was already set to '+arrow_status)
                    return redirect('/changevote/?target='+str(target_pk))   

                message_string = 'Type:ChangeVote,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Target:'+target_pk+',Vote:'+arrow_status
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn')
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='ChangeVote',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_arrowupdate = ArrowUpdate.objects.create(txn=new_txn,arrow=arrow,arrowupdate=new_status)

                target.update_balance_due(current_time)
                old_is_good = target.is_good()
                old_net = target.net_votes
                old_matched = target.matched_count

                target.net_votes += new_status - arrow.status
                target.good = target.is_good()

                if new_status == 0:
                    arrow.position = None
                else:
                    arrow.position = target.last_position + 1
                    target.last_position += 1

                if new_status*(arrow.status - old_net) > 0:  #i.e unmatched not empty
                    unmatched = Arrow.objects.filter(target = target, cancelled = False, matched = False, status = -new_status).exclude(source = sender).order_by('position')  #-pos?no
                    first_match = unmatched[0]
                    first_match.matched = True
                    arrow.matched = True
                    target.matched_count += 1
                    first_match.save()

                if old_matched == 0 and target.matched_count > 0:
                    target.settlement_countdown = current_time

                if old_matched > 0 and target.is_good() != old_is_good:
                    target.settlement_countdown = current_time
                   
                #assert target.zone() == 'Good' or target.zone() == 'Bad'

                arrow.status = new_status
                sender.sequence_next += 1
                arrow.save()
                target.save()
                sender.save()
                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/changevote/?target='+str(target_pk))

        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/changevote/') 
            return render(request, 'core/changevote.html',{'form_errors':form.errors})
    else:
        target_pk = request.GET.get('target')
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/changevote.html',{'account':account,'target_pk':target_pk})
        else:
            return render(request, 'core/changevote.html',{'target_pk':target_pk})



def challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            account_1 = form.cleaned_data.get('account_1') 
            account_2 = form.cleaned_data.get('account_2') 
            signature = form.cleaned_data.get('signature')
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().get(pk=1) 
                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/challenge/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/challenge/')
                if sender.balance < constants.CHALLENGER_BET:
                    messages.error(request, 'Transaction was unsuccessful. Need a balance of at least {} to make a challenge.'.format(constants.CHALLENGER_BET))
                    return redirect('/challenge/')

                if sender.registered == True and sender.balance < constants.MIN_BALANCE + constants.CHALLENGER_BET: 
                    messages.error(request, 'Transaction was unsuccessful. Registered accounts must have a minimum balance of {}.'.format(constants.MIN_BALANCE))
                    return redirect('/changevote-challenge/')

                try:
                    account1 = Account.objects.get(public_key = account_1)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Account 1 does not exist.')
                    return redirect('/challenge/')
                try:
                    account2 = Account.objects.get(public_key = account_2)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Account 2 does not exist.')
                    return redirect('/challenge/')

                if account1 == account2:
                    messages.error(request, 'Transaction was unsuccessful. Account 1 and Account 2 cannot be the same')
                    return redirect('/challenge/')

                if account1.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. Account 1 is not registered')
                    return redirect('/challenge/')    

                if account2.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. Account 2  is not registered')
                    return redirect('/challenge/')

                if account1.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. Account 1 is already suspended')
                    return redirect('/challenge/')    

                if account2.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. Account 2  is already suspended')
                    return redirect('/challenge/')

                if Challenge.objects.filter((Q(defendant_1=account1) & Q(defendant_2=account2)) | (Q(defendant_1=account2) & Q(defendant_2=account1)) & Q(finished=False)& Q(cancelled=False)).exists():
                    messages.error(request, 'Transaction was unsuccessful. A challenge against those two accounts already exists.')
                    return redirect('/challenge/')


                current_time = timezone.now()
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                message_string = 'Type:Challenge,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Account1:'+account_1+',Account2:'+account_2                        
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
               

                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='Challenge',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_challenge = Challenge.objects.create(challenger=sender,defendant_1=account1,defendant_2=account2,created=current_time)
                new_challenge_creation = ChallengeCreation.objects.create(txn=new_txn,challenge=new_challenge,amount=constants.CHALLENGER_BET)

                sender.balance -= constants.CHALLENGER_BET

                sender.sequence_next += 1
                sender.save()

                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/challenge/')
        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/challenge/') 
            return render(request, 'core/challenge.html',{'form_errors':form.errors})
    else:
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/challenge.html',{'account':account})
        else:
            return render(request, 'core/challenge.html')
            

def updatechallengevote(request):
    if request.method == 'POST':
        form = ChallengeLinkUpdateForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            challenge_id = form.cleaned_data.get('challenge_id') 
            vote = form.cleaned_data.get('vote') 
            choice = form.cleaned_data.get('choice') 
            signature = form.cleaned_data.get('signature')
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1
                current_time = timezone.now()

                if current_time < last_txn.event.timestamp:
                    messages.error(request, 'Transaction was unsuccessful. Wrong datetime.')  #should really never happen
                    return redirect('/changevote-challenge/')
                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/changevote-challenge/')
                
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/changevote-challenge/')

                if sender.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. The sender account is suspended.')
                    return redirect('/changevote/')

                if sender.balance < constants.MIN_BALANCE: 
                    messages.error(request, 'Transaction was unsuccessful. Account balance is less that the required minimum.')
                    return redirect('/changevote-challenge/')
               
                try:
                    challenge = Challenge.objects.get(id = challenge_id, finished= False, cancelled=False)
                except Challenge.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such challenge exists.')
                    return redirect('/changevote-challenge/')        

                try:
                    challengelink = ChallengeLink.objects.get(voter = sender, challenge = challenge, finished = False, cancelled = False)
                except ChallengeLink.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such active challengelink exists.')
                    return redirect('/changevote-challenge/')        

                new_status = 1 if vote == 'Trust' else -1 if vote == 'Distrust' else 0 if vote == 'Neutral' else 9
                new_choice = 1 if choice == 'Account1' else -1 if choice == 'Account2' else 0 if choice == 'Neutral' else 9

                if challengelink.matched == True and new_status != challengelink.status:
                    messages.error(request, 'Transaction was unsuccessful. You cannot change your vote as it has already been matched.')
                    return redirect('/changevote-challenge/?id='+str(challenge_id))

                if challengelink.matched_who == True and challengelink.status_who != new_choice:
                    messages.error(request, 'Transaction was unsuccessful. You cannot change your choice as it has already been matched.')
                    return redirect('/changevote-challenge/?id='+str(challenge_id))

                if challengelink.status == new_status and challengelink.status_who == new_choice:
                    messages.error(request, 'Nothing changed as your transaction did not change anthing.')
                    return redirect('/changevote-challenge/?id='+str(challenge_id))   

                message_string = 'Type:ChangeChallengeVote,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',ChallengeID:'+str(challenge_id)+',Vote:'+vote+',Choice:'+choice
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn')
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='ChangeChallengeVote',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_challengelinkupdate = ChallengeLinkUpdate.objects.create(txn=new_txn,challengelink=challengelink,challengelinkupdate=new_status,challengelink_who_update=new_choice)


                if challengelink.status != new_status:
                    old_is_good = challenge.is_good()
                    old_net = challenge.net_votes
                    old_matched = challenge.matched_count
                    challenge.net_votes += new_status - challengelink.status
                    challenge.good = challenge.is_good()

                    if new_status == 0:
                        challengelink.position = None
                    else:
                        challengelink.position = challenge.last_position + 1
                        challenge.last_position += 1

                    if new_status*(challengelink.status - old_net) > 0:  #i.e unmatched not empty
                        unmatched = ChallengeLink.objects.filter(challenge = challenge, cancelled=False, matched = False, status = -new_status).exclude(voter = sender).order_by('position')  #-pos?no
                        first_match = unmatched[0]
                        first_match.matched = True
                        challengelink.matched = True
                        challenge.matched_count += 1
                        first_match.save()

                    if old_matched == 0 and challenge.matched_count > 0:
                        challenge.settlement_countdown = current_time

                    if old_matched > 0 and challenge.is_good() != old_is_good:
                        challenge.settlement_countdown = current_time
                
                if challengelink.status_who != new_choice:
                    old_net_who = challenge.net_votes_who
                    old_matched_who = challenge.matched_count_who
                    challenge.net_votes_who += new_choice - challengelink.status_who                    

                    if new_choice == 0:
                        challengelink.position_who = None
                    else:
                        challengelink.position_who = challenge.last_position_who + 1
                        challenge.last_position_who += 1

                    if new_choice*(challengelink.status_who - old_net_who) > 0:  #i.e unmatched not empty
                        unmatched = ChallengeLink.objects.filter(challenge = challenge, cancelled=False, matched_who = False, status_who = -new_choice).exclude(voter = sender).order_by('position_who')  #-pos?no
                        first_match_who = unmatched[0]
                        first_match_who.matched_who = True
                        challengelink.matched_who = True
                        challenge.matched_count_who += 1
                        first_match_who.save()


                challengelink.status = new_status
                challengelink.status_who = new_choice
                sender.sequence_next += 1
                challengelink.save()
                challenge.save()
                sender.save()
                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/changevote-challenge/?id='+str(challenge_id))

        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/changevote/') 
            return render(request, 'core/changevote-challenge.html',{'form_errors':form.errors})
    else:
        challenge_id = request.GET.get('id')
        form = ChallengeLinkUpdateForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/changevote-challenge.html',{'account':account,'challenge_id':challenge_id})
        else:
            return render(request, 'core/changevote-challenge.html')

