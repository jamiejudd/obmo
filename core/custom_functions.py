from core.models import Account,Arrow,EventCounter,Event,Txn,Transfer,Registration,ArrowUpdate

from django.db.models import Q

from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from django.contrib import messages
#from django.contrib.messages import get_messages

from django.utils import timezone

import nacl.signing
from nacl.hash import sha512
import nacl.encoding
import nacl.exceptions
import binascii

def create_arrow(u1,u2):
	