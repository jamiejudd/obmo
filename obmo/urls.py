from django.conf.urls import url
from core import views as core_views
from django.contrib.auth import views as auth_views
#from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings

# from django_private_chat import urls as django_private_chat_urls

urlpatterns = [
    url(r'^$', core_views.index, name='index'),

    url(r'^accounts/$', core_views.accounts, name='accounts'),
    url(r'^accounts/(?P<username>[\dabcdefABCDEF]{64})/$', core_views.account, name='account'),  
    url(r'^accounts/(?P<username>[\dabcdefABCDEF]{64})/history/$', core_views.account_history, name='account_history'), 

    url(r'^myaccount/$', core_views.myaccount,  name='myaccount'),
    url(r'^myaccount/history/$', core_views.myaccount_history,  name='myaccount_history'),

    url(r'^challenges/$', core_views.challenges, name='challenges'),
    url(r'^challenges/(?P<challengeid>[1-9][0-9]*)/$', core_views.single_challenge, name='single_challenge'), 
    url(r'^challenges/(?P<challengeid>[1-9][0-9]*)/history/$', core_views.single_challenge_history, name='single_challenge_history'), 

    url(r'^transactions/$', core_views.txns, name='txns'),  #explore txnchain
    url(r'^transactions/(?P<txno>[1-9][0-9]*)/$', core_views.txn, name='txn'), 

    url(r'^statistics/$', core_views.statistics, name='statistics'),
    url(r'^exchange2/$', core_views.exchange2, name='exchange2'),
    url(r'^exchange/$', core_views.exchange, name='exchange'),
    url(r'^faq/$', core_views.faq, name='faq'),
    url(r'^newkeypair/$', core_views.newkeypair, name='newkeypair'),
    url(r'^retrievepubkey/$', core_views.retrievepubkey, name='retrievepubkey'),

    url(r'^login/$', auth_views.LoginView.as_view(),  name='login'),
    #url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    url(r'^logout/$',core_views.logout_view, name='logout'),

    url(r'^transfer/$', core_views.transfer, name='transfer'),
    url(r'^register/$', core_views.register, name='register'),
    url(r'^commit/$', core_views.commit, name='commit'),
    url(r'^reveal/$', core_views.reveal, name='reveal'),
    url(r'^changevote/$', core_views.arrowupdate, name='arrowupdate'),
    url(r'^challenge/$', core_views.challenge, name='challenge'),
    url(r'^changevote-challenge/$', core_views.updatechallengevote, name='updatechallengevote'),
    url(r'^resetpassword/$', core_views.resetpassword, name='resetpassword'),

    #url(r'^chatmessages/$', core_views.chatmessages, name='chatmessages'),  
    url(r'^offer/$', core_views.offer, name='offer'),  
    url(r'^offer/delete/$', core_views.offer_delete, name='offer_delete'),  
    url(r'^mark_read/$', core_views.mark_read, name='mark_read'),  

    #url(r'^', include('django_private_chat.urls')),
    # path('', include('django_private_chat.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
