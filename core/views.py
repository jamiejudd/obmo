from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import Account,Arrow,EventCounter,Event,Txn,Transfer,Registration,ArrowUpdate,BalanceUpdate,Commitment,Revelation
from core.forms import  RegisterForm,TransferForm,UserRegistrationForm,ResetPasswordForm,CommitForm,RevealForm,ArrowUpdateForm
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


#GETS
def index(request):
    return render(request, 'core/index.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def exchange(request):
    #return render(request, 'core/transactions.html')
    accounts = Account.objects.all()
    arrows = Arrow.objects.all()
    event_counters = EventCounter.objects.all()
    events = Event.objects.all()
    txns = Txn.objects.all()
    registrations = Registration.objects.all()
    transfers = Transfer.objects.all()
    arrow_updates = ArrowUpdate.objects.all()
    balance_updates = BalanceUpdate.objects.all()
    commitments = Commitment.objects.all()
    revelations = Revelation.objects.all()

    return render(request, 'core/transaction.html',{'accounts':accounts,'arrows':arrows,'commitments':commitments,'revelations':revelations,'event_counters':event_counters,'events':events,'txns':txns,'registrations':registrations,'transfers':transfers,'arrow_updates':arrow_updates,'balance_updates':balance_updates})
    #return render(request, 'core/index2.html')
    
def statistics(request):
    arrows = Arrow.objects.all()
    return render(request, 'core/transactions.html',{'arrows':arrows})
    
def accounts(request):
    accounts_all = Account.objects.all().order_by('-balance')
    # try:
    #     per_page = int(request.REQUEST['count'])
    # except:
    #     per_page = 1     # default value
    paginator = Paginator(accounts_all, 5) # Show 25 contacts per page, too many -> loads slowly
    page = request.GET.get('page')
    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        accounts = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/accounts.html', {'accounts':accounts})

def account(request,username):
    account = Account.objects.get(public_key=username)
    arrows = Arrow.objects.filter(target=account)
    return render(request, 'core/account.html',{'username':username,'account':account,'arrows':arrows})
    
def account_history(request,username):
    account = Account.objects.get(public_key=username)
    txns_all = Txn.objects.select_related('event').filter(Q(sender=account) | Q(recipient=account)| Q(recipient=account) ).order_by('-id')
    paginator = Paginator(txns_all, 4) 
    page = request.GET.get('page')
    try:
        txns = paginator.page(page)
    except PageNotAnInteger:
        txns = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        txns = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/account_history.html',{'username':username,'txns':txns})    

@login_required 
def myaccount_history(request):
    account = Account.objects.get(public_key=request.user.username)
    txns_all = Txn.objects.filter(Q(sender=account) | Q(recipient=account)| Q(recipient=account) ).order_by('-id')
    paginator = Paginator(txns_all, 4) 
    page = request.GET.get('page')
    try:
        txns = paginator.page(page)
    except PageNotAnInteger:
        txns = paginator.page(1)# If page is not an integer, deliver first page.
    except EmptyPage:
        txns = paginator.page(paginator.num_pages)# If page is out of range (e.g. 9999), deliver last page of results.
    return render(request, 'core/account_history.html',{'username':request.user.username,'txns':txns})    

def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return '{:d} hours'.format(hours)
    else:
        return '{:02d} minutes'.format( minutes)

@login_required 
def myaccount(request):
    account = Account.objects.get(public_key=request.user.username)
    arrows = Arrow.objects.filter(target=account)
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
    return render(request, 'core/myaccount.html',{'username':request.user.username,'account':account,'arrows':arrows,'time_status':time_status,'timer':timer})
    #return HttpResponseRedirect('/accounts/%s/' % request.user.username )

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


def commit(request):
    if request.method == 'POST':
        form = CommitForm(request.POST)
        if form.is_valid():
            sender_pk = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            committed_hash = form.cleaned_data.get('committed_hash') 
            signature = form.cleaned_data.get('signature')
            with transaction.atomic():
                #event_counter = EventCounter.objects.select_for_update().get(pk=1)  #nowait=true??
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??

                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/commit/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/commit/')
                if sender.registered == False:
                    messages.error(request, 'Transaction was unsuccessful. You need to be registered to submit random numbers.')
                    return redirect('/commit/')
                if sender.committed == True:
                    messages.error(request, 'Transaction was unsuccessful. Already have a commited value. Reveal first..')
                    return redirect('/commit/')

                current_time = timezone.now()
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
                #event_counter = EventCounter.objects.select_for_update().get(pk=1)  #nowait=true??
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??

                try:
                    sender = Account.objects.get(public_key = sender_pk)
                except Account.DoesNotExist:
                    messages.error(request, 'Transaction was unsuccessful. Sender does not exist.')
                    return redirect('/reveal/')
                if sender.sequence_next != sender_seq_no:
                    messages.error(request, 'Transaction was unsuccessful. Incorrect sequence number.')
                    return redirect('/reveal/')
                if sender.committed == False:
                    messages.error(request, 'Transaction was unsuccessful. First you need to commited a value.')
                    return redirect('/reveal/')

                revealed_value_bytes = bytes.fromhex(revealed_value)
                hash_value = nacl.hash.sha512(revealed_value_bytes, encoder=nacl.encoding.RawEncoder)
     
                if sender.committed_hash != hash_value.hex():
                    messages.error(request, 'Transaction was unsuccessful. Incorrect value for hash.')
                    return redirect('/reveal/')

                current_time = timezone.now()
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

                if commitment.committed_hash != sender.committed_hash:
                    messages.error(request, 'Transaction was unsuccessful. Serious problemo.')
                    return redirect('/reveal/')

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
                #event_counter = EventCounter.objects.select_for_update().get(pk=1)  #nowait=true??
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??

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
                
                current_time = timezone.now()
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                message_string = 'Type:Transfer,Sender:'+sender_pk+',SeqNo:'+str(sender_seq_no)+',Recipient:'+recipient_pk+',Amount:'+str(amount)                         
                txn_data = '"TxnNo":"'+str(txn_number)+'","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"'+last_txn.txn_hash+'"'
                txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
                try:
                    recipient = Account.objects.get(public_key = recipient_pk)
                except Account.DoesNotExist:
                    recipient = Account.objects.create(public_key = recipient_pk)

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
        form = TransferForm()
        if request.user.is_authenticated:
            account = Account.objects.get(public_key = request.user.username)
            return render(request, 'core/transfer.html',{'account':account})
        else:
            return render(request, 'core/transfer.html')
            #return render(request, 'core/transfer.html',{'form':form})


def register(request):
    if request.method == 'POST':
        # print(request.POST)
        # print(request.POST['username'])
        # print(request.POST['password1'])
        form = RegisterForm(request.POST,request.FILES)
        userform = UserRegistrationForm(request.POST)
        if userform.is_valid() and form.is_valid():
            # print('userform.cleaned_data')
            # print(userform.cleaned_data)
            # print('form.cleaned_data')
            # print(form.cleaned_data)
            #txn_type = form.cleaned_data.get('txn_type') 
            username = form.cleaned_data.get('username') 
            sender_seq_no = form.cleaned_data.get('sender_seq_no') 
            name = form.cleaned_data.get('name') 
            #scan img upload with antivirus, at the end save it with standardized file name
            photo = form.cleaned_data.get('photo') 
            photo_hash = form.cleaned_data.get('photo_hash') 
            signature = form.cleaned_data.get('signature')

            # #if its the first registration use this code
            # with transaction.atomic():
            #     event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
            #     sender = Account.objects.create(public_key=username,balance=100)
            #     current_time = timezone.now()
            #     message_string = 'Type:Register,PublicKey:'+username+',SeqNo:1,Name:'+name+',PhotoHash:'+photo_hash
            #     txn_data = '"TxnNo":"1","Created":"'+str(current_time.strftime("%Y-%m-%d-%H:%M:%S"))+'","Message":"'+message_string+'","Signature":"'+signature+'","PreviousHash":"Genesis"'
            #     txn_hash  = nacl.hash.sha512(txn_data.encode('utf-8'), encoder=nacl.encoding.RawEncoder)
            #     new_event = Event.objects.create(id=1,timestamp=current_time, event_type='Txn') #handle integrity error for create
            #     new_txn = Txn.objects.create(id=1,event=new_event,txn_previous_hash='Genesis',txn_type='Register',sender=sender,sender_seq_no=sender_seq_no,txn_message=message_string,signature=signature,txn_data=txn_data,txn_hash=txn_hash.hex())
            #     new_registration = Registration.objects.create(txn=new_txn,name=name,photo_hash=photo_hash)
            #     sender.name = name
            #     sender.photo = photo
            #     sender.photo_hash = photo_hash
            #     sender.registered = True
            #     sender.registered_date = current_time
            #     sender.linked = True
            #     sender.verified = True
            #     sender.sequence_next += 1
            #     userform.save()
            #     sender.save()
            #     event_counter.last_event_no += 1
            #     event_counter.save()

            with transaction.atomic():
                event_counter = EventCounter.objects.select_for_update().first()  #nowait=true??
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
                          

                current_time = timezone.now()
                last_txn = Txn.objects.last()
                txn_number = last_txn.id+1

                if current_time <= last_txn.event.timestamp:
                    messages.error(request, 'Transaction was unsuccessful. Wrong datetime.')  #should really never happen
                    return redirect('/register/')

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
            return render(request, 'core/register.html',{'form_errors':form.errors})
            #return redirect('/register/') 
    else:
        form = RegisterForm()
        return render(request, 'core/register.html')



def arrowupdate(request):
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
                        elapsed_time_seconds = Decimal(elapsed_time.total_seconds())
                        dividend = elapsed_time_seconds*Decimal(0.0011574074)  # 100/24*3600=0.0011574074
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




#-----this is the old transfer view, before moving to forms----


# def transfer(request):
#     if request.method == 'POST':
#         form = TransferForm(request.POST)
#         if form.is_valid():
#             txn_type = form.cleaned_data.get('txn_type') 
#             sender_pk = form.cleaned_data.get('sender') 
#             sender_seq_no = form.cleaned_data.get('sender_seq_no') 
#             recipient_pk = form.cleaned_data.get('recipient') 
#             amount = form.cleaned_data.get('amount') 
#             signature = form.cleaned_data.get('signature')

#             #put all these checks in a seperate file?? or not?? in forms file?

#             if txn_type == 'Transfer':
#                 pass
#             else:
#                 messages.error(request, 'Transaction type should be transfer')
#                 return redirect('/transfer/unsuccessful') 

#             if sender_pk == recipient_pk:
#                 messages.error(request, 'Recipient cannot be the same as Sender.')
#                 return redirect('/transfer/unsuccessful') 

#             if len(sender_pk) == 64: 
#                 pass
#             else:
#                 messages.error(request, 'sender_pk not 64 chars long')
#                 return redirect('/transfer/unsuccessful') 

#             if len(recipient_pk) == 64: 
#                 pass
#             else:
#                 messages.error(request, 'recipient_pk not 64 chars long')
#                 return redirect('/transfer/unsuccessful') 
            
#             #len sig=128
            
#             try:
#                 sender_pk_decoded = binascii.unhexlify(sender_pk) 
#             except binascii.Error as err: 
#                 messages.error(request, 'sender_pk is not a proper hex string:  ')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/transfer/unsuccessful')   

#             try:
#                 recipient_pk_decoded = binascii.unhexlify(recipient_pk) 
#             except binascii.Error as err: 
#                 messages.error(request, 'recipient_pk is not a proper hex string:  ')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/transfer/unsuccessful')                 



#             try:
#                 verify_key = nacl.signing.VerifyKey(sender_pk,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
#             except nacl.exceptions.CryptoError as err:
#                 messages.error(request, 'problem creating verify key (serious!!):  ')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/transfer/unsuccessful')  

#             message_string = '{"Type":"Transfer","Sender":"'+sender_pk+'","SeqNo":'+str(sender_seq_no)+',"Recipient":"'+recipient_pk+'","Amount":'+str(amount)+'}'   #bad name?
#             #print(message_string.encode('utf-8').hex())
#             #print(bytearray.fromhex(sender_pk).hex())

#             try:
#                 signature_bytes = bytes.fromhex(signature)
#             except ValueError as err:
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/transfer/unsuccessful') 

#             try:
#                 message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
#             except Exception as err:
#                 messages.error(request, 'message_string_encoded not working .')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/transfer/unsuccessful') 

#             try:
#                 verify_key.verify(message_string_encoded, signature_bytes)  
#             except nacl.exceptions.BadSignatureError:
#                 messages.error(request, 'Incorrect signature.')
#                 return redirect('/transfer/unsuccessful') 



#             #now that weve passed all checks, try to do the txn , move some of these functions to model methods?

#             with transaction.atomic():
#                 txn_counter = TxnCounter.objects.select_for_update().get(pk=1)  #nowait=true??
#                 last_txn = Txn.objects.get(txn_number = txn_counter.last_txn_no)

#                 try:
#                     sender = Account.objects.get(public_key = sender_pk)
#                 except Account.DoesNotExist:
#                     messages.error(request, 'no such sender account.')
#                     return redirect('/transfer/unsuccessful')
                
#                 if sender.sequence_next == sender_seq_no:
#                     pass
#                 else:
#                     messages.error(request, 'Incorrect sequence number')
#                     return redirect('/transfer/unsuccessful')

#                 if sender.balance > amount: #txnfees
#                     pass
#                 else:
#                     messages.error(request, 'Insufficient balance')
#                     return redirect('/transfer/unsuccessful')
                

#                 # DO THE TXN:
#                 txn_number = last_txn.txn_number + 1
#                 current_time = timezone.now()

#                 if current_time > last_txn.txn_timestamp:
#                     pass
#                 else:
#                     messages.error(request, 'bad time')
#                     return redirect('/transfer/unsuccessful')

#                 txn_string = '{"TxnNo":'+str(txn_number)+',"Created":"'+str(current_time)+'","Type":"Transfer","Sender":"'+sender_pk+'","SeqNo":'+str(sender_seq_no)+',"Recipient":"'+recipient_pk+'","Amount":'+str(amount)+',"Signature":"'+signature+'","PrevHash":"'+last_txn.txn_hash+'"}'
#                 txn_hash  = nacl.hash.sha512(txn_string.encode('utf-8'), encoder=nacl.encoding.HexEncoder)

#                 try:
#                     recipient = Account.objects.get(public_key = recipient_pk)
#                 except Account.DoesNotExist:
#                     recipient = Account(public_key = recipient_pk, balance = 0 , sequence_next = 1)
#                     recipient.save()
              
#                 new_transfer = Transfer(sender=sender, sender_seq_no=sender_seq_no, recipient=recipient, amount=amount, signature=signature, timestamp=current_time, txn_number=txn_number)
#                 new_transaction = Txn(txn_number=txn_number, txn_hash=txn_hash, txn_data=txn_string, txn_type='T')
#                 sender.balance -= amount
#                 recipient.balance += amount
#                 sender.sequence_next += 1
#                 txn_counter.last_txn_no += 1
#                 sender.save()
#                 recipient.save()
#                 new_transfer.save()
#                 new_transaction.save()
#                 txn_counter.save()

#             return redirect('/transfer/success')

#         else:
#             messages.error(request, 'form not valid')
#             return redirect('/transfer/unsuccessful') 
#     else:
#         return render(request, 'core/transfer.html')
























# def register(request):
#     if request.method == 'POST':
#         # print('request.POST')
#         # print(request.POST)
#         # print(request.POST['username'])
#         # print(request.POST['password1'])
#         form = RegisterForm(request.POST,request.FILES)
#         userform = UserRegistrationForm(request.POST)
#         if userform.is_valid() and form.is_valid():
#             # print('userform.cleaned_data')
#             # print(userform.cleaned_data)
#             # print('form.cleaned_data')
#             # print(form.cleaned_data)
#             txn_type = form.cleaned_data.get('txn_type') 
#             sender_pk = form.cleaned_data.get('username') 
#             sender_seq_no = form.cleaned_data.get('sender_seq_no') 
#             name = form.cleaned_data.get('name') 
#             #scan img upload with antivirus, at the end save it with standardized file name
#             photo = form.cleaned_data.get('photo') 
#             photo_hash = form.cleaned_data.get('photo_hash') 
#             signature = form.cleaned_data.get('signature')


#             if txn_type == 'Register':
#                 pass
#             else:
#                 messages.error(request, 'Transaction type should be register')
#                 return redirect('/register/unsuccessful') 

#             if len(sender_pk) == 64: 
#                 pass
#             else:
#                 messages.error(request, 'sender_pk not 64 chars long')
#                 return redirect('/register/unsuccessful') 
            
#             #len sig=128

#             try:
#                 sender_pk_decoded = binascii.unhexlify(sender_pk) 
#             except binascii.Error as err: 
#                 messages.error(request, 'sender_pk is not a proper hex string:  ')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/register/unsuccessful')   

#             try:
#                 verify_key = nacl.signing.VerifyKey(sender_pk,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
#             except nacl.exceptions.CryptoError as err:
#                 messages.error(request, 'problem creating verify key (serious!!):  ')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/register/unsuccessful')  

#             message_string = '{"Type":"Register","PubKey":"'+sender_pk+'","SeqNo":'+str(sender_seq_no)+',"Name":"'+name+'","PhotoHash":"'+photo_hash+'"}'   #bad name?
#             print(message_string)
#             print(message_string.encode('utf-8').hex())
#             print(bytearray.fromhex(sender_pk).hex())


#             try:
#                 signature_bytes = bytes.fromhex(signature)
#             except ValueError as err:
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/register/unsuccessful') 

#             try:
#                 message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
#             except Exception as err:
#                 messages.error(request, 'message_string_encoded not working .')
#                 messages.error(request, type(err).__name__)
#                 messages.error(request, err)
#                 return redirect('/register/unsuccessful') 

#             try:
#                 verify_key.verify(message_string_encoded, signature_bytes)  
#             except nacl.exceptions.BadSignatureError:
#                 messages.error(request, 'Incorrect signature.')
#                 return redirect('/register/unsuccessful') 


#             #try perform txn
#             with transaction.atomic():
#                 txn_counter = TxnCounter.objects.select_for_update().get(pk=1)  #nowait=true??
#                 last_txn = Txn.objects.get(txn_number = txn_counter.last_txn_no)

#                 try:
#                     sender = Account.objects.get(public_key = sender_pk)
#                 except Account.DoesNotExist:
#                     messages.error(request, 'no such sender account.')
#                     return redirect('/register/unsuccessful')
                
#                 if sender.sequence_next == sender_seq_no:
#                     pass
#                 else:
#                     messages.error(request, 'Incorrect sequence number')
#                     return redirect('/register/unsuccessful')                
#                 if sender.registered == False:
#                     pass
#                 else:
#                     messages.error(request, 'That pk is already registered')
#                     return redirect('/register/unsuccessful')

#                 parameter_group = Parameter.objects.get(pk=1) 
#                 minbal = parameter_group.beta
#                 if sender.balance >= minbal: #txnfees
#                     pass
#                 else:
#                     messages.error(request, 'Insufficient minimum balance')
#                     return redirect('/register/unsuccessful')
                

#                 # DO THE TXN:
#                 txn_number = last_txn.txn_number + 1
#                 current_time = timezone.now()

#                 if current_time > last_txn.txn_timestamp:
#                     pass
#                 else:
#                     messages.error(request, 'bad time')
#                     return redirect('/register/unsuccessful')

#                 txn_string = '{"TxnNo":'+str(txn_number)+',"Created":"'+str(current_time)+'","Type":"Register","Sender":"'+sender_pk+'","SeqNo":'+str(sender_seq_no)+',"Name":"'+name+'","PhotoHash":'+photo_hash+',"Signature":"'+signature+'","PrevHash":"'+last_txn.txn_hash+'"}'
#                 txn_hash  = nacl.hash.sha512(txn_string.encode('utf-8'), encoder=nacl.encoding.HexEncoder)

#                 new_registeration = Registration(sender=sender, sender_seq_no=sender_seq_no, name=name, photo_hash=photo_hash, signature=signature, timestamp=current_time, txn_number=txn_number)
#                 new_transaction = Txn(txn_number=txn_number, txn_hash=txn_hash, txn_data=txn_string, txn_type='R')
           
#                 sender.name = name
#                 sender.photo = photo
#                 sender.photo_hash = photo_hash
#                 sender.registered = True
#                 sender.sequence_next += 1
#                 txn_counter.last_txn_no += 1

#                 userform.save()

#                 sender.save()
#                 new_registeration.save()
#                 new_transaction.save()
#                 txn_counter.save()

#             return redirect('/register/success')

#         else:
#             messages.error(request, 'form not valid')
#             return redirect('/register/unsuccessful') 
#     else:
#         form = RegisterForm()
#         return render(request, 'core/register.html', {'form': form})

