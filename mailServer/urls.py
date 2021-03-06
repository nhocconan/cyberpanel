from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.loadEmailHome, name='loadEmailHome'),
    url(r'^createEmailAccount', views.createEmailAccount, name='createEmailAccount'),
    url(r'^submitEmailCreation', views.submitEmailCreation, name='submitEmailCreation'),


    ## Delete email
    url(r'^deleteEmailAccount', views.deleteEmailAccount, name='deleteEmailAccount'),
    url(r'^getEmailsForDomain$', views.getEmailsForDomain, name='getEmailsForDomain'),
    url(r'^submitEmailDeletion', views.submitEmailDeletion, name='submitEmailDeletion'),


    ## Change email password
    url(r'^changeEmailAccountPassword', views.changeEmailAccountPassword, name='changeEmailAccountPassword'),
    url(r'^submitPasswordChange', views.submitPasswordChange, name='submitPasswordChange'),

    ## DKIM Manager

    url(r'^dkimManager', views.dkimManager, name='dkimManager'),
    url(r'^fetchDKIMKeys', views.fetchDKIMKeys, name='fetchDKIMKeys'),
    url(r'^generateDKIMKeys$', views.generateDKIMKeys, name='generateDKIMKeys'),

    url(r'^installOpenDKIM', views.installOpenDKIM, name='installOpenDKIM'),
    url(r'^installStatusOpenDKIM', views.installStatusOpenDKIM, name='installStatusOpenDKIM'),

]