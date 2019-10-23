from django import forms            
from django.contrib.auth.models import User   # fill in custom user info then save it 
from django.contrib.auth.forms import UserCreationForm     

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii




class CommitForm(forms.Form):
    username = forms.CharField(label='Sender', min_length=64, max_length=64)
    sender_seq_no = forms.IntegerField(label='Seq No.')
    committed_hash = forms.CharField(label='committed_hash', min_length=128, max_length=128)
    signature = forms.CharField(label='Signature', min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no', 'committed_hash','signature')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("username is not a proper hex string:: ")
        #except all other errors?
        return username

    def clean_committed_hash(self):
        committed_hash = self.cleaned_data['committed_hash']
        try:
            committed_hash_decoded = binascii.unhexlify(committed_hash) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("committed_hash is not a proper hex string:: ")
        #except all other errors?
        return committed_hash

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        committed_hash = cleaned_data.get("committed_hash")
        signature = cleaned_data.get("signature")
        if username and committed_hash:
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                #messages.error(request, 'problem creating verify key (serious!!):  ')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem creating verify key (serious!!): ")
            #except all other errors? shouldnt be any other error right?

            message_string = 'Type:Commit,Sender:'+username+',SeqNo:'+str(sender_seq_no)+',Hash:'+committed_hash   #bad name?

            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem with sig ")

            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                #messages.error(request, 'message_string_encoded not working .')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                #messages.error(request, 'Incorrect signature.')
                raise forms.ValidationError("Incorrect signature.")



class RevealForm(forms.Form):
    username = forms.CharField(label='Sender', min_length=64, max_length=64)
    sender_seq_no = forms.IntegerField(label='Seq No.')
    revealed_value = forms.CharField(label='revealed_value', min_length=128, max_length=128)
    signature = forms.CharField(label='Signature', min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no', 'revealed_value','signature')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("username is not a proper hex string:: ")
        #except all other errors?
        return username

    def clean_revealed_value(self):
        revealed_value = self.cleaned_data['revealed_value']
        try:
            revealed_value_decoded = binascii.unhexlify(revealed_value) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("revealed_value is not a proper hex string:: ")
        #except all other errors?
        return revealed_value

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        revealed_value = cleaned_data.get("revealed_value")
        signature = cleaned_data.get("signature")
        if username and revealed_value:
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                #messages.error(request, 'problem creating verify key (serious!!):  ')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem creating verify key (serious!!): ")
            #except all other errors? shouldnt be any other error right?

            message_string = 'Type:Reveal,Sender:'+username+',SeqNo:'+str(sender_seq_no)+',Value:'+revealed_value   #bad name?

            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem with sig ")

            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                #messages.error(request, 'message_string_encoded not working .')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                #messages.error(request, 'Incorrect signature.')
                raise forms.ValidationError("Incorrect signature.")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password2']


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=64,  max_length=64)
    sender_seq_no = forms.IntegerField()
    name = forms.CharField(min_length=4, max_length=20)
    photo = forms.ImageField()
    photo_hash = forms.CharField(min_length=128, max_length=128)
    signature = forms.CharField(min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no','name','photo','photo_hash','signature')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            print(2) #messages.error(request, err)
            raise forms.ValidationError("Public Key is not a proper hex string:: ")
        #except all other errors?
        return username

    def clean_name(self):
        name = self.cleaned_data['name']
        if name == 'badname':
            raise forms.ValidationError("name should be good")
        return name

    def clean_photo(self):
        photo = self.cleaned_data['photo']
        if 1>2:
            raise forms.ValidationError("photo should be good")
        return photo

    def clean_photo_hash(self):
        photo_hash = self.cleaned_data['photo_hash']
        if 1>2:
            raise forms.ValidationError("photo_hash should be good")
        return photo_hash

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        name = cleaned_data.get("name")
        photo = cleaned_data.get("photo")
        photo_hash = cleaned_data.get("photo_hash")
        signature = cleaned_data.get("signature")
        if username and sender_seq_no and name and photo and photo_hash and signature:

            #CHECK HASH(PHOTO)==PHOTOHASH
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                #messages.error(request, 'problem creating verify key (serious!!):  ')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem creating verify key, serious!")
            #except all other errors? shouldnt be any other error right?

            message_string = 'Type:Register,PublicKey:'+username+',SeqNo:'+str(sender_seq_no)+',Name:'+name+',PhotoHash:'+photo_hash   #bad name? escape chars?
            # print(message_string)
            # print(message_string.encode('utf-8').hex())
            # print(bytearray.fromhex(username).hex())

            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem with sig ")

            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                #messages.error(request, 'message_string_encoded not working .')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                #messages.error(request, 'Incorrect signature.')
                raise forms.ValidationError("Incorrect signature.")




class TransferForm(forms.Form):
    username = forms.CharField(label='Sender', min_length=64, max_length=64)
    sender_seq_no = forms.IntegerField(label='Seq No.')
    recipient_pk = forms.CharField(label='Recipient', min_length=64, max_length=64)
    amount = forms.DecimalField(label='Amount', max_digits = 20, decimal_places = 2)
    signature = forms.CharField(label='Signature', min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no', 'recipient_pk','amount','signature')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("username is not a proper hex string:: ")
        #except all other errors?
        return username

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0.01:
            raise forms.ValidationError("Amount cannot be less than 0.01")
        return amount

    def clean_recipient_pk(self):
        recipient_pk = self.cleaned_data['recipient_pk']
        try:
            recipient_pk_decoded = binascii.unhexlify(recipient_pk) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("recipient_pk is not a proper hex string:: ")
        #except all other errors?
        return recipient_pk

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        recipient_pk = cleaned_data.get("recipient_pk")
        amount = cleaned_data.get("amount")
        signature = cleaned_data.get("signature")
        if username and recipient_pk:
            if username == recipient_pk:
                raise forms.ValidationError("recipient_pk is same as username")
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                #messages.error(request, 'problem creating verify key (serious!!):  ')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem creating verify key (serious!!): ")
            #except all other errors? shouldnt be any other error right?

            message_string = 'Type:Transfer,Sender:'+username+',SeqNo:'+str(sender_seq_no)+',Recipient:'+recipient_pk+',Amount:'+str(amount)   #bad name?

            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem with sig ")

            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                #messages.error(request, 'message_string_encoded not working .')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                #messages.error(request, 'Incorrect signature.')
                raise forms.ValidationError("Incorrect signature.")


class ArrowUpdateForm(forms.Form):
    username = forms.CharField(min_length=64, max_length=64)
    sender_seq_no = forms.IntegerField()
    target_pk = forms.CharField(min_length=64, max_length=64)
    arrow_status_choices = (('Neutral', 'Neutral'),('Trust', 'Trust'),('Distrust', 'Distrust'))   #does this give error if arrow_status = "Trustish"
    arrow_status = forms.ChoiceField(choices = arrow_status_choices)
    signature = forms.CharField(min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no','target_pk','arrow_status','signature')


    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("username is not a proper hex string")
        #except all other errors?
        return username

    def clean_target_pk(self):
        target_pk = self.cleaned_data['target_pk']
        try:
            target_pk_decoded = binascii.unhexlify(target_pk) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("target_pk is not a proper hex string:: ")
        #except all other errors?
        return target_pk

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        target_pk = cleaned_data.get("target_pk")
        arrow_status = cleaned_data.get("arrow_status")
        signature = cleaned_data.get("signature")
        if username and target_pk:
            if username == target_pk:
                raise forms.ValidationError("target_pk is same as username")
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                raise forms.ValidationError("problem creating verify key serious!")
            message_string = 'Type:ChangeVote,Sender:'+username+',SeqNo:'+str(sender_seq_no)+',Target:'+target_pk+',Vote:'+arrow_status   #bad name?
            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                raise forms.ValidationError("problem with sig ")
            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                raise forms.ValidationError("Incorrect signature.")


class OfferForm(forms.Form):
    offer = forms.CharField(label='Offer', max_length=120)

    class Meta:
        fields = ('offer')




class ResetPasswordForm(forms.Form):
    username = forms.CharField(label='Public Key',min_length=64,  max_length=64)
    new_password = forms.CharField(min_length=3, max_length=40)
    signature = forms.CharField(label='Signature', min_length=128, max_length=128)

    class Meta:
        fields = ('username', 'new_password','signature')

    def clean_public_key(self):
        username = self.cleaned_data['username']
        try:
            public_key_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("Public Key is not a proper hex string:: ")
        #except all other errors?
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        new_password = cleaned_data.get("new_password")
        signature = cleaned_data.get("signature")
        if username and new_password and signature:
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                #messages.error(request, 'problem creating verify key (serious!!):  ')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem creating verify key (serious!!): ")
            #except all other errors? shouldnt be any other error right?

            message_string = 'Type:PasswordReset,PublicKey:'+username+',NewPassword:'+new_password
            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem with sig ")

            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                #messages.error(request, 'message_string_encoded not working .')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                #messages.error(request, 'Incorrect signature.')
                raise forms.ValidationError("Incorrect signature.")






class ChallengeForm(forms.Form):
    username = forms.CharField(label='Sender', min_length=64, max_length=64)
    sender_seq_no = forms.IntegerField(label='Seq No.')
    account_1 = forms.CharField(label='Account 1', min_length=64, max_length=64)
    account_2 = forms.CharField(label='Account 2', min_length=64, max_length=64)
    signature = forms.CharField(label='Signature', min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no', 'account_1','account_2','signature')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("username is not a proper hex string:: ")
        #except all other errors?
        return username

    def clean_account_1(self):
        account_1 = self.cleaned_data['account_1']
        try:
            account_1_decoded = binascii.unhexlify(account_1) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("account_1 is not a proper hex string:: ")
        #except all other errors?
        return account_1

    def clean_account_2(self):
        account_2 = self.cleaned_data['account_2']
        try:
            account_2_decoded = binascii.unhexlify(account_2) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("account_2 is not a proper hex string:: ")
        #except all other errors?
        return account_2

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        account_1 = cleaned_data.get("account_1")
        account_2 = cleaned_data.get("account_2")
        signature = cleaned_data.get("signature")
        if username and account_1 and account_2:
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                #messages.error(request, 'problem creating verify key (serious!!):  ')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem creating verify key (serious!!): ")
            #except all other errors? shouldnt be any other error right?

            message_string = 'Type:Challenge,Sender:'+username+',SeqNo:'+str(sender_seq_no)+',Account1:'+account_1+',Account2:'+account_2  #bad name?

            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("problem with sig ")

            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                #messages.error(request, 'message_string_encoded not working .')
                #messages.error(request, type(err).__name__)
                #messages.error(request, err)
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                #messages.error(request, 'Incorrect signature.')
                raise forms.ValidationError("Incorrect signature.")


class ChallengeLinkUpdateForm(forms.Form):
    username = forms.CharField(min_length=64, max_length=64)
    sender_seq_no = forms.IntegerField()
    challenge_id = forms.IntegerField()
    vote_choices = (('Neutral', 'Neutral'),('Trust', 'Trust'),('Distrust', 'Distrust'))   #does this give error if arrow_status = "Trustish"
    vote = forms.ChoiceField(choices = vote_choices)
    choice_choices = (('Neutral', 'Neutral'),('Account1', 'Account1'),('Account2', 'Account2'))   #does this give error if arrow_status = "Trustish"
    choice = forms.ChoiceField(choices = choice_choices)
    signature = forms.CharField(min_length=128, max_length=128)

    class Meta:
        fields = ('username','sender_seq_no','challenge_id','vote','choice','signature')


    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username_decoded = binascii.unhexlify(username) #no need new variable
        except binascii.Error as err: 
            #messages.error(request, err)
            raise forms.ValidationError("username is not a proper hex string")
        #except all other errors?
        print(username)
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        sender_seq_no = cleaned_data.get("sender_seq_no")
        challenge_id = cleaned_data.get("challenge_id")
        vote = cleaned_data.get("vote")
        choice = cleaned_data.get("choice")
        signature = cleaned_data.get("signature")
        if username and challenge_id:
            try:
                verify_key = nacl.signing.VerifyKey(username,encoder=nacl.encoding.HexEncoder) # Create a VerifyKey object from a hex serialized public key
            except nacl.exceptions.CryptoError as err:
                raise forms.ValidationError("problem creating verify key serious!")
            message_string = 'Type:ChangeChallengeVote,Sender:'+username+',SeqNo:'+str(sender_seq_no)+',ChallengeID:'+str(challenge_id)+',Vote:'+vote+',Choice:'+choice   #bad name?
            try:
                signature_bytes = bytes.fromhex(signature)
            except ValueError as err:
                raise forms.ValidationError("problem with sig ")
            try:
                message_string_encoded = message_string.encode(encoding='utf-8',errors='strict')
            except Exception as err:
                raise forms.ValidationError("message_string_encoded not working ")
            try:
                verify_key.verify(message_string_encoded, signature_bytes)  
            except nacl.exceptions.BadSignatureError:
                raise forms.ValidationError("Incorrect signature.")
