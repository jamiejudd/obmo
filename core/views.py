from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404


from core.models import Account,Arrow,Challenge,ChallengeLink,EventCounter,Event,Txn,Registration,Transfer,Commitment,Revelation,ArrowUpdate,ChallengeCreation,BalanceUpdate,ArrowCreation,MarketSettlement,MarketSettlementTransfer
from core.forms import  RegisterForm,TransferForm,UserRegistrationForm,ResetPasswordForm,CommitForm,RevealForm,ArrowUpdateForm,ChallengeForm
import core.constants as constants

from django.db.models import Q

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
#GETS
def index(request):
    return render(request, 'core/index.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def accounts(request):
    accounts_all = Account.objects.order_by('-registered','-id')
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
    score = account.verification_score()
    # if account.linked == True:
    #     score = int(100*account.net_votes/account.degree)
    countdown = None
    total_seconds = None
    if account.settlement_countdown is not None:
        td = account.settlement_countdown + timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME) - timezone.now()
        countdown = format_timedelta(td)
        total_seconds = td.total_seconds()
    return render(request, 'core/account.html',{'username':username,'account':account,'arrows':arrows,'score':score,'countdown':countdown,'total_seconds':total_seconds})
    
def account_history(request,username):
    try:
        account = Account.objects.get(public_key=username)
    except Account.DoesNotExist:
        raise Http404("Account does not exist")
    events_all = Event.objects.prefetch_related('txn','txn__transfer','txn__registration','txn__commitment','txn__revelation','txn__arrowupdate','arrowcreation').filter(Q(txn__sender=account) | Q(txn__transfer__recipient=account) | Q(txn__arrowupdate__arrow__target=account) | Q(arrowcreation__arrow__source=account) | Q(marketsettlement__account=account) | Q(marketsettlementtransfer__payee=account) ).order_by('-id')
    paginator = Paginator(events_all, 54) 
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        events = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/account_history.html',{'username':username,'events':events})    
    
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
    challenges_all = Challenge.objects.all().order_by('id')
    paginator = Paginator(challenges_all, 5) # Show 25 contacts per page, too many -> loads slowly
    page = request.GET.get('page')
    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        challenges = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        challenges = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/challenges.html', {'challenges':challenges})

def single_challenge(request,challengeid):
    challenge = Challenge.objects.get(id=challengeid)
    return render(request, 'core/single_challenge.html',{'challengeid':challengeid,'challenge':challenge})

def exchange(request):
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
    #tasks = Task.objects.all()

    return render(request, 'core/exchange.html',{'accounts':accounts,'arrows':arrows,'challenges':challenges,'challengelinks':challengelinks,'commitments':commitments,'revelations':revelations,'event_counters':event_counters,'events':events,'txns':txns,'registrations':registrations,'transfers':transfers,'arrow_updates':arrow_updates,'balance_updates':balance_updates,'MarketSettlementTransfers':MarketSettlementTransfers,'MarketSettlements':MarketSettlements})
    #return render(request, 'core/index2.html')
    
def statistics(request):
    arrows = Arrow.objects.all()
    #return render(request, 'core/transactions.html',{'arrows':arrows})
    return render(request, 'core/daterange.html',{'arrows':arrows})
    

def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return '{:2}d {:2}h {:2}m {:2}s'.format(int(days),int(hours), int(minutes), int(seconds))

@login_required 
def myaccount(request):
    account = Account.objects.get(public_key=request.user.username)
    arrows = Arrow.objects.filter(target=account)
    challengelinks = ChallengeLink.objects.filter(voter=account)


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
    return render(request, 'core/myaccount.html',{'username':request.user.username,'account':account,'arrows':arrows,'challengelinks':challengelinks,'time_status':time_status,'timer':timer})
    #return HttpResponseRedirect('/accounts/%s/' % request.user.username )

   
@login_required 
def myaccount_history(request):
    account = Account.objects.get(public_key=request.user.username)
    events_all = Event.objects.prefetch_related('txn','txn__transfer','txn__registration','txn__commitment','txn__revelation','txn__arrowupdate','arrowcreation').filter(Q(txn__sender=account) | Q(txn__transfer__recipient=account) | Q(txn__arrowupdate__arrow__target=account) | Q(arrowcreation__arrow__source=account) ).order_by('-id')
    paginator = Paginator(events_all, 18) 
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        events = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/account_history.html',{'username':request.user.username,'events':events})    

def newkeypair(request):
    return render(request, 'core/newkeypair.html')

def retrievepubkey(request):
    return render(request, 'core/retrievepubkey.html')

def faq(request):
    return render(request, 'core/faq.html')

#POSTS
def resetpassword(request):
    if request.method == 'POST':
        print(request.POST)
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data.get('username') 
            new_password = form.cleaned_data.get('new_password') 
            signature = form.cleaned_data.get('signature')

            #move this to form checks?
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

# def donexttask(request):
#     if request.method == 'POST':
#         next_task = Task.objects.filter(completed = False).order_by("time_due").first()
#         if next_task is not None and next_task.time_due <  timezone.now():
#            next_task.doit()
#         return redirect('/donexttask/')
#     else:
#         return render(request, 'core/donexttask.html')


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
                #event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                current_time = timezone.now()
                print('commmit started: '+str(current_time)+' evtno: '+str(event_counter.last_event_no))
                try:
                    sender = Account.objects.select_for_update().get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    print('TXN FAILED. COMMIT. NO ACC')
                    return redirect('/commit/')
                print(' seqno: '+str(sender_seq_no)+' seqnet: '+str(sender.sequence_next))
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    print('TXN FAILED. COMMIT. INC SEQ')
                    return redirect('/commit/')
                if sender.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. You need to be registered to submit random numbers.')
                    print('TXN FAILED. COMMIT. NOT REGD')
                    return redirect('/commit/')
                if sender.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. This account is suspended.')
                    print('TXN FAILED. COMMIT. suspd')
                    return redirect('/commit/')
                if sender.committed == True:
                    messages.error(request, 'Transaction was unsuccessful. Already have a commited value. Reveal first..')
                    print('TXN FAILED. COMMIT. REV FIRST')
                    return redirect('/commit/')

                try:
                    last_txn = Txn.objects.last()
                    txn_number = last_txn.id+1

                    message_string = 'Type:Commit,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Hash:'+committed_hash                       
                    txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                    txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)

                    new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn') #handle integrity error for create
                    new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='Commitment',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                    new_commitment = Commitment.objects.create(txn=new_txn,committed_hash=committed_hash)

                    sender.committed = True
                    print('committed set to true')
                    sender.committed_time = current_time
                    sender.committed_hash = committed_hash
                    sender.sequence_next += 1
                    sender.save()
                    print('sender saved com '+str(timezone.now()))
                    ss = Account.objects.get(public_key = sender_pk)
                    print('ss '+str(ss.committed))

                    event_counter.last_event_no += 1
                    event_counter.save()
                    print('txn completed')
                except:
                    print('TXN FAILED. COMMIT. EXECEPTION')
                print('commit finished {}'.format(timezone.now()))


            messages.success(request, 'Transaction was successful.')
            return redirect('/commit/')
        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/commit/') 
            print('TXN FAILED. COMMIT. FORM NOT VALID')
            return render(request, 'core/commit.html',{'form_errors':form.errors})
    else:
        form = CommitForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/commit.html',{'account':account})
        else:
            return render(request, 'core/commit.html')
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
                #print('start txn reveal')
                event_counter = EventCounter.objects.select_for_update().get(pk=1)
                #event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                current_time = timezone.now()
                print('reveal started '+str(current_time)+' '+str(event_counter.last_event_no))
                try:
                    sender = Account.objects.select_for_update().get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    print('TXN FAILED. REEVEAL. NO SENDER')
                    return redirect('/reveal/')
                except:
                    print('BADD ERROR EXECPTION')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    print('TXN FAILED. REEVEAL. INC SEQ')
                    return redirect('/reveal/')
                if sender.committed == False:
                    messages.error(request, 'Transaction was unsuccessful. First you need to commited a value.')
                    print('TXN FAILED. REEVEAL. COMMIT FIRST '+str(sender.committed) )
                    return redirect('/reveal/')
                if sender.suspended == True:
                    messages.error(request, 'Transaction was unsuccessful. This account is suspended.')
                    print('TXN FAILED. REEVEAL. suspd')
                    return redirect('/reveal/')

                revealed_value_bytes = bytes.fromhex(revealed_value)
                hash_value = nacl.hash.sha512(revealed_value_bytes, encoder=nacl.encoding.RawEncoder)
     
                if sender.committed_hash != hash_value.hex():
                    messages.error(request, 'Transaction was unsuccessful. Incorrect value for hash.')
                    print('TXN FAILED. REEVEAL. INC HASH')
                    return redirect('/reveal/')

                if current_time < sender.committed_time + timezone.timedelta(seconds=constants.TIMEDELTA_1_HOURS) :
                    messages.error(request, 'Transaction was unsuccessful. Reveal too soon.')
                    print('TXN FAILED. REEVEAL. 2SSON')
                    return redirect('/reveal/')
                
                print('timedif rreveael '+str((current_time-sender.committed_time - timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS)).total_seconds() ))
                if current_time > sender.committed_time + timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS) :
                    messages.error(request, 'Transaction was unsuccessful. Reveal too late.')
                    print('TXN FAILED. REEVEAL. 2LATE ')
                    return redirect('/reveal/')

                try:
                    commitment = Commitment.objects.filter(txn__sender = sender).last()
                except Commitment.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Serious problem, couldnt find commitment.')
                    print('TXN FAILED. REEVEAL. NOFIND')
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
                print('committed set to false')
                sender.sequence_next += 1
                sender.save()
                print('sender saved rev'+str(timezone.now()))

                event_counter.last_event_no += 1
                event_counter.save()
                print('reveal finished {}'.format(timezone.now()))

            messages.success(request, 'Transaction was successful.')
            return redirect('/reveal/')
        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/reveal/') 
            print('TXN FAILED. REVEAL. FORM NOT VALID')
            return render(request, 'core/reveal.html',{'form_errors':form.errors})
    else:
        form = RevealForm()
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
                    print('TXN FAILED. T NO ACC')
                    return redirect('/transfer/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    print('TXN FAILED. T INC SEQ')
                    return redirect('/transfer/')
                if sender.balance < amount:
                    messages.error(request, 'Transaction was unsuccessful. Insufficient balance')
                    print('TXN FAILED. T LOW BAL')
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
            print('TXN FAILED. FORM NOT VALID')
            return render(request, 'core/transfer.html',{'form_errors':form.errors})
    else:
        form = TransferForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/transfer.html',{'account':account})
        else:
            return render(request, 'core/transfer.html')
            #return render(request, 'core/transfer.html',{'form':form})


def register(request):
    if request.method == 'POST':
        #print(request.POST)
        #print(request.FILES)
        #print('POST register:   '+request.POST['username'])
        form = RegisterForm(request.POST,request.FILES)
        userform = UserRegistrationForm(request.POST)
        if userform.is_valid() and form.is_valid():
            # print('userform.cleaned_data')
            # print(userform.cleaned_data)
            # print('form.cleaned_data')
            # print(form.cleaned_data)
            username = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            name = form.cleaned_data.get('name') 
            #scan img upload with antivirus, at the end save it with standardized file name
            photo = form.cleaned_data.get('photo') 
            photo_hash = form.cleaned_data.get('photo_hash') 
            signature = form.cleaned_data.get('signature')
            
            #current_time = timezone.now()
            #do_tasks(current_time)


            if Account.objects.count() == 0:
                with transaction.atomic():
                    event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                    current_time = timezone.now()
                    sender = Account.objects.create(public_key=username,balance=10000,balance_due_last_updated = current_time, committed = False)
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
                        print('TXN FAILED. NO ACC')
                        return redirect('/register/')
                    if sender.sequence_next != sender_seq_no:
                        messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                        print('TXN FAILED. INC SEQ NO')
                        return redirect('/register/') 
                    if sender.registered == True:
                        messages.error(request, 'Transaction was unsuccessful. That account is already registered.')
                        print('TXN FAILED. ALREADY REG')
                        return redirect('/register/')
                    if sender.balance < constants.MIN_BALANCE: #txnfees?
                        messages.error(request, 'Transaction was unsuccessful. Account balance is less that the required minimum.')
                        print('TXN FAILED. LOW BAL')
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

                    #Task.objects.create(time_due=current_time+timezone.timedelta(seconds=constants.TIMEDELTA_2_HOURS), action='CreateLinks', account=sender)

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
            print('TXN FAILED. FORM NOT VALID')
            return render(request, 'core/register.html',{'form_errors':form.errors})
            #return redirect('/register/') 
    else:
        form = RegisterForm()
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
                    print('TXN FAILED. AU. NOSNDER')
                    return redirect('/changevote/')
                
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    print('TXN FAILED. AU. INC SEQ')
                    return redirect('/changevote/')

                if sender.balance >= 0: #txnfees?
                    pass
                else:
                    messages.error(request, 'Transaction was unsuccessful. Insufficient balance')
                    print('TXN FAILED. AU. LOW BAL')
                    return redirect('/changevote/')
               
                try:
                    target = Account.objects.get(public_key = target_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such target account exists.')
                    print('TXN FAILED. AU. NO TARGET')
                    return redirect('/changevote/')        

                try:
                    arrow = Arrow.objects.get(source = sender, target = target, expired = False)
                except Arrow.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such active Arrow exists.')
                    print('TXN FAILED. AU. NO AROW')
                    return redirect('/changevote/')        

                if arrow.matched == True:
                    messages.error(request, 'Transaction was unsuccessful. You cannot change your vote/bet as it has already been matched.')
                    print('TXN FAILED. AU. MATCHED ROI')
                    return redirect('/changevote/')

                new_status = 1 if arrow_status == 'Trust' else -1 if arrow_status == 'Distrust' else 0 if arrow_status == 'Neutral' else 9

                if arrow.status == new_status:
                    messages.error(request, 'Nothing changed as your vote was already set to '+arrow_status)
                    print('TXN FAILED. AU. SAMEY')
                    return redirect('/changevote/?target='+str(target_pk))   

                message_string = 'Type:ChangeVote,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Target:'+target_pk+',Vote:'+arrow_status
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn')
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='ChangeVote',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_arrowupdate = ArrowUpdate.objects.create(txn=new_txn,arrow=arrow,arrowupdate=new_status)


                target.update_balance_due(current_time)
                old_zone = target.zone()
                old_net = target.net_votes
                old_matched = target.matched_count

                target.net_votes += new_status - arrow.status

                if new_status == 0:
                    arrow.position = None
                else:
                    arrow.position = target.last_position + 1
                    target.last_position += 1

                if new_status*(arrow.status - old_net) > 0:  #i.e unmatched not empty
                    unmatched = Arrow.objects.filter(target = target, expired = False, matched = False, status = -new_status).exclude(source = sender).order_by('position')  #-pos?no
                    first_match = unmatched[0]
                    first_match.matched = True
                    arrow.matched = True
                    target.matched_count += 1
                    first_match.save()

                if old_matched == 0 and target.matched_count > 0:
                    target.settlement_countdown = current_time
                    #Task.objects.create(time_due=current_time+timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME), account=target, action='SettleMkt',)

                if old_matched > 0 and target.zone() != old_zone:
                    target.settlement_countdown = current_time
                    #old_task = Task.objects.get(account=target,completed=False,action='SettleMkt')
                    #old_task.delete()
                    #Task.objects.create(time_due=current_time+timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME), account=target, action='SettleMkt',)
                
                assert target.zone() == 'Good' or target.zone() == 'Bad'

                arrow.status = new_status
                sender.sequence_next += 1
                arrow.save()
                target.save()
                sender.save()
                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/changevote/')

        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/changevote/') 
            print('TXN FAILED. AU. FORM NOT VALID')
            return render(request, 'core/changevote.html',{'form_errors':form.errors})
    else:
        target_pk = request.GET.get('target')
        form = ArrowUpdateForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/changevote.html',{'account':account,'target_pk':target_pk})
        else:
            return render(request, 'core/changevote.html')



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
                #event_counter = EventCounter.objects.select_for_update().get(pk=1)  #nowait=true??
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??

                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/challenge/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/challenge/')
                if sender.balance < constants.CHALLENGER_BET:
                    messages.error(request, 'Transaction was unsuccessful. Insufficient balance')
                    return redirect('/challenge/')
                try:
                    account1 = Account.objects.get(public_key = account_1)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. account_1 does not exist.')
                    return redirect('/challenge/')
                try:
                    account2 = Account.objects.get(public_key = account_2)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. account_2 does not exist.')
                    return redirect('/challenge/')

                if account1 == account2:
                    messages.error(request, 'Transaction was unsuccessful. Cant bbe same')
                    return redirect('/challenge/')

                if account1.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. account1 is not registered')
                    return redirect('/challenge/')    

                if account2.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. account2  is not registered')
                    return redirect('/challenge/')

                if Challenge.objects.filter((Q(defendant_1=account1) & Q(defendant_2=account2)) | (Q(defendant_1=account2) & Q(defendant_2=account1))).exists():
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
                new_challenge_creation = ChallengeCreation.objects.create(txn=new_txn,defendant_1=account1,defendant_2=account2)

                new_challenge = Challenge.objects.create(challenger=sender,defendant_1=account1,defendant_2=account2,created=current_time)

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
        form = ChallengeForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/challenge.html',{'account':account})
        else:
            return render(request, 'core/challenge.html')
            #return render(request, 'core/challenge.html',{'form':form})
            

def updatechallengevote(request):
    if request.method == 'POST':
        print(request.POST)
        print(request.POST['arrow_status'])
        form = ArrowUpdateForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            target_pk = form.cleaned_data.get('target_pk') 
            arrow_status = form.cleaned_data.get('arrow_status') 
            signature = form.cleaned_data.get('signature')
            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1
                current_time = timezone.now()

                if current_time < last_txn.event.timestamp:
                    messages.error(request, 'Transaction was unsuccessful. Wrong datetime.')  #should really never happen
                    return redirect('/changevote/')
                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/changevote/')
                
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/changevote/')

                if sender.balance >= 0: #txnfees?
                    pass
                else:
                    messages.error(request, 'Transaction was unsuccessful. Insufficient balance')
                    return redirect('/changevote/')
               
                try:
                    target = Account.objects.get(public_key = target_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such target account exists.')
                    return redirect('/changevote/')        

                try:
                    arrow = Arrow.objects.get(source = sender, target = target, expired = False)
                except Arrow.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. No such active Arrow exists.')
                    return redirect('/changevote/')        

                if arrow.matched == True:
                    messages.error(request, 'Transaction was unsuccessful. You cannot change your vote/bet as it has already been matched.')
                    return redirect('/changevote/')

                if target.settlement_countdown and (target.settlement_countdown < current_time - timezone.timedelta(seconds=constants.MARKET_SETTLEMENT_TIME)):
                    print('we need to settle at least one market')
                    messages.error(request, 'Transaction was unsuccessful. This market has just completed.')
                    return redirect('/changevote/')

                new_status = 1 if arrow_status == 'Trust' else -1 if arrow_status == 'Distrust' else 0 if arrow_status == 'Neutral' else 9
                print('new_status: '+str(new_status))

                if arrow.status == new_status:
                    print('samesame')
                    messages.error(request, 'Nothing changed as your vote was already set to '+arrow_status)
                    return redirect('/changevote/?target='+str(target_pk))   

                message_string = 'Type:ChangeVote,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Target:'+target_pk+',Vote:'+arrow_status
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                new_event = Event.objects.create(id=event_counter.last_event_no+1,timestamp=current_time, event_type='Txn')
                new_txn = Txn.objects.create(id=txn_number,event=new_event,txn_previous_hash=last_txn.txn_hash,txn_type='ChangeVote',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
                new_arrowupdate = ArrowUpdate.objects.create(txn=new_txn,arrow=arrow,arrowupdate=new_status)

                old_zone = target.zone()
                old_net = target.net_votes
                target.net_votes += new_status - arrow.status
                print('old_zone: '+str(old_zone))
                print('old_net: '+str(old_net))
                print('target.net_votes: '+str(target.net_votes))
                print('target.zone: '+str(target.zone))
                if new_status*(arrow.status - old_net) > 0:  #i.e unmatched not empty
                    print('unmatched: '+str(new_status*(arrow.status - old_net)))
                    unmatched = Arrow.objects.filter(target=target,expired=False,matched=False,status= -new_status).exclude(source=sender).order_by('position')
                    first_match = unmatched[0]
                    first_match.matched = True
                    arrow.matched = True
                    target.matched_count += 1
                    print('target.zone: '+str(target.zone))
                    if (target.matched_count == 1) or (target.zone != old_zone):
                        target.settlement_countdown = current_time
                    first_match.save()
                else:
                    arrow.position = target.last_position + 1
                    target.last_position += 1
                    if target.zone != old_zone:
                        target.settlement_countdown = current_time

                if target.zone != old_zone:
                    if (old_zone == 'Good'):
                        elapsed_time = current_time - target.balance_due_last_updated 
                        dividend = Decimal(elapsed_time.total_seconds())*Decimal(constants.UBI_RATE/24/3600)
                        target.balance_due += dividend
                        #target.total_ubi_generated += dividend
                        target.balance_due_last_updated = current_time
                        target.save()
                    else:
                        target.balance_due_last_updated = current_time
                        target.save()


                arrow.status = new_status
                sender.sequence_next += 1
                arrow.save()
                target.save()
                sender.save()
                event_counter.last_event_no += 1
                event_counter.save()

            messages.success(request, 'Transaction was successful.')
            return redirect('/changevote/')

        else:
            messages.error(request, 'Transaction was unsuccessful. Form not valid.') #repeats same msg multiple times, need to clear msgs at right time
            #return redirect('/changevote/') 
            return render(request, 'core/changevote.html',{'form_errors':form.errors})
    else:
        target_pk = request.GET.get('target')
        form = ArrowUpdateForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/changevote.html',{'account':account,'target_pk':target_pk})
        else:
            return render(request, 'core/changevote.html')

