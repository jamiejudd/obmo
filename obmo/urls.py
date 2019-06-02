"""ubicoin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
#from django.contrib import admin  #we dont want an admin site?
from core import views as core_views
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^$', core_views.index, name='index'),

    url(r'^accounts/$', core_views.accounts, name='accounts'),
    url(r'^accounts/(?P<username>[\dabcdefABCDEF]{64})/$', core_views.account, name='account'),  #last!!??
    url(r'^accounts/(?P<username>[\dabcdefABCDEF]{64})/history/$', core_views.account_history, name='account_history'),  #last!!??

    url(r'^myaccount/$', core_views.myaccount,  name='myaccount'),
    url(r'^myaccount/history/$', core_views.myaccount_history,  name='myaccount_history'),

    #url(r'^challenges/$', core_views.challenges, name='challenges'),
    #url(r'^challenges/(?P<challengeid>[\dabcdefABCDEF]{64})/$', core_views.single_challenge, name='single_challenge'),  #last!!??

    url(r'^transactions/$', core_views.txns, name='txns'),  #explore txnchain
    url(r'^transactions/(?P<txno>[1-9][0-9]*)/$', core_views.txn, name='txn'),  #last!!??

    url(r'^statistics/$', core_views.statistics, name='statistics'),
    url(r'^exchange/$', core_views.exchange, name='exchange'),
    url(r'^faq/$', core_views.faq, name='faq'),
    url(r'^newkeypair/$', core_views.newkeypair, name='newkeypair'),
    url(r'^retrievepubkey/$', core_views.retrievepubkey, name='retrievepubkey'),

    url(r'^login/$', auth_views.login,  name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

    url(r'^transfer/$', core_views.transfer, name='transfer'),
    url(r'^register/$', core_views.register, name='register'),
    url(r'^commit/$', core_views.commit, name='commit'),
    url(r'^reveal/$', core_views.reveal, name='reveal'),
    url(r'^changevote/$', core_views.arrowupdate, name='arrowupdate'),
    # url(r'^challenge/$', core_views.challenge, name='challenge'),
    # url(r'^changevote-challenge/$', core_views.updatevote, name='updatevote'),
    url(r'^resetpassword/$', core_views.resetpassword, name='resetpassword'),

    #url(r'^admin/', admin.site.urls),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
