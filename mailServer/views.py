# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse
from models import Domains,EUsers
# Create your views here.
from loginSystem.models import Administrator
from websiteFunctions.models import Websites
from loginSystem.views import loadLoginPage
import plogical.CyberCPLogFileWriter as logging
import json
import shlex
import subprocess
from plogical.virtualHostUtilities import virtualHostUtilities
from plogical.mailUtilities import mailUtilities
import thread
from dns.models import Domains as dnsDomains
from dns.models import Records as dnsRecords
import os

def loadEmailHome(request):
    try:
        val = request.session['userID']
        return render(request, 'mailServer/index.html')
    except KeyError:
        return redirect(loadLoginPage)


def createEmailAccount(request):
    try:
        val = request.session['userID']
        try:
            admin = Administrator.objects.get(pk=request.session['userID'])

            if admin.type == 1:
                websites = admin.websites_set.all()
            else:
                websites = Websites.objects.filter(admin=admin)

            websitesName = []

            for items in websites:
                websitesName.append(items.domain)

            return render(request, 'mailServer/createEmailAccount.html', {'websiteList':websitesName})
        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(str(msg))
            return HttpResponse(str(msg))

    except KeyError:
        return redirect(loadLoginPage)


def submitEmailCreation(request):
    try:
        if request.method == 'POST':

            data = json.loads(request.body)
            domainName = data['domain']
            userName = data['username']
            password = data['password']

            ## Check if already exists

            finalEmailUsername = userName + "@" + domainName

            if EUsers.objects.filter(email=finalEmailUsername).exists():
                data_ret = {'createEmailStatus': 0, 'error_message': "This account already exists!"}
                json_data = json.dumps(data_ret)
                return HttpResponse(json_data)

            ## Check for email limits.

            website = Websites.objects.get(domain=domainName)

            try:

                newEmailDomain = Domains(domainOwner=website, domain=domainName)
                newEmailDomain.save()

                if website.package.emailAccounts == 0 or (
                            newEmailDomain.eusers_set.all().count() < website.package.emailAccounts):
                    pass
                else:
                    data_ret = {'createEmailStatus': 0,
                                'error_message': "Exceeded maximum amount of email accounts allowed for the package."}
                    json_data = json.dumps(data_ret)
                    return HttpResponse(json_data)

            except:

                emailDomain = Domains.objects.get(domain=domainName)

                if website.package.emailAccounts == 0 or (
                    emailDomain.eusers_set.all().count() < website.package.emailAccounts):
                    pass
                else:
                    data_ret = {'createEmailStatus': 0,
                                'error_message': "Exceeded maximum amount of email accounts allowed for the package."}
                    json_data = json.dumps(data_ret)
                    return HttpResponse(json_data)


            ## Create email entry

            execPath = "sudo python " + virtualHostUtilities.cyberPanel + "/plogical/mailUtilities.py"

            execPath = execPath + " createEmailAccount --domain " + domainName

            output = subprocess.check_output(shlex.split(execPath))

            if output.find("1,None") > -1:

                emailDomain = Domains.objects.get(domain=domainName)

                emailAcct = EUsers(emailOwner=emailDomain, email=finalEmailUsername, password=password)
                emailAcct.save()

                data_ret = {'createEmailStatus': 1, 'error_message': "None"}
                json_data = json.dumps(data_ret)
                return HttpResponse(json_data)

            else:
                data_ret = {'createEmailStatus': 0, 'error_message': output}
                json_data = json.dumps(data_ret)
                return HttpResponse(json_data)

            ## create email entry ends



    except BaseException, msg:
        data_ret = {'createEmailStatus': 0, 'error_message': str(msg)}
        json_data = json.dumps(data_ret)
        return HttpResponse(json_data)


def deleteEmailAccount(request):
    try:
        val = request.session['userID']
        try:
            admin = Administrator.objects.get(pk=request.session['userID'])

            if admin.type == 1:
                websites = admin.websites_set.all()
            else:
                websites = Websites.objects.filter(admin=admin)

            websitesName = []

            for items in websites:
                websitesName.append(items.domain)

            return render(request, 'mailServer/deleteEmailAccount.html', {'websiteList':websitesName})
        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(str(msg))
            return HttpResponse(str(msg))

    except KeyError:
        return redirect(loadLoginPage)



def getEmailsForDomain(request):
    try:
        val = request.session['userID']
        try:
            if request.method == 'POST':

                data = json.loads(request.body)
                domain = data['domain']

                domain = Domains.objects.get(domain=domain)

                emails = domain.eusers_set.all()

                if emails.count() == 0:
                    final_dic = {'fetchStatus': 0, 'error_message': "No email accounts exits"}

                    final_json = json.dumps(final_dic)

                    return HttpResponse(final_json)

                json_data = "["
                checker = 0

                for items in emails:
                    dic = {'email': items.email}

                    if checker == 0:
                        json_data = json_data + json.dumps(dic)
                        checker = 1
                    else:
                        json_data = json_data + ',' + json.dumps(dic)

                json_data = json_data + ']'

                final_dic = {'fetchStatus': 1, 'error_message': "None", "data": json_data}

                final_json = json.dumps(final_dic)

                return HttpResponse(final_json)


        except BaseException,msg:
            data_ret = {'fetchStatus': 0, 'error_message': str(msg)}
            json_data = json.dumps(data_ret)
            return HttpResponse(json_data)
    except KeyError,msg:
        data_ret = {'fetchStatus': 0, 'error_message': str(msg)}
        json_data = json.dumps(data_ret)
        return HttpResponse(json_data)


def submitEmailDeletion(request):
    try:
        val = request.session['userID']
        try:
            if request.method == 'POST':

                data = json.loads(request.body)
                email = data['email']

                email = EUsers(email=email)

                email.delete()

                data_ret = {'deleteEmailStatus': 1, 'error_message': "None"}
                json_data = json.dumps(data_ret)
                return HttpResponse(json_data)



        except BaseException,msg:
            data_ret = {'deleteEmailStatus': 0, 'error_message': str(msg)}
            json_data = json.dumps(data_ret)
            return HttpResponse(json_data)
    except KeyError,msg:
        data_ret = {'deleteEmailStatus': 0, 'error_message': str(msg)}
        json_data = json.dumps(data_ret)
        return HttpResponse(json_data)



#######


def changeEmailAccountPassword(request):
    try:
        val = request.session['userID']
        try:
            admin = Administrator.objects.get(pk=request.session['userID'])

            if admin.type == 1:
                websites = admin.websites_set.all()
            else:
                websites = Websites.objects.filter(admin=admin)

            websitesName = []

            for items in websites:
                websitesName.append(items.domain)

            return render(request, 'mailServer/changeEmailPassword.html', {'websiteList':websitesName})
        except BaseException, msg:
            logging.CyberCPLogFileWriter.writeToFile(str(msg))
            return HttpResponse(str(msg))

    except KeyError:
        return redirect(loadLoginPage)


def submitPasswordChange(request):
    try:
        val = request.session['userID']
        try:
            if request.method == 'POST':
                data = json.loads(request.body)

                domain = data['domain']
                email = data['email']
                password = data['password']

                dom = Domains(domain=domain)

                emailAcct = EUsers(email=email)
                emailAcct.delete()

                emailAcct = EUsers(emailOwner=dom, email=email, password=password)
                emailAcct.save()

                data_ret = {'passChangeStatus': 1, 'error_message': "None"}
                json_data = json.dumps(data_ret)
                return HttpResponse(json_data)



        except BaseException,msg:
            data_ret = {'passChangeStatus': 0, 'error_message': str(msg)}
            json_data = json.dumps(data_ret)
            return HttpResponse(json_data)
    except KeyError,msg:
        data_ret = {'passChangeStatus': 0, 'error_message': str(msg)}
        json_data = json.dumps(data_ret)
        return HttpResponse(json_data)

#######

def dkimManager(request):
    try:
        val = request.session['userID']

        openDKIMInstalled = 0

        if mailUtilities.checkIfDKIMInstalled() == 1:
            openDKIMInstalled = 1

            admin = Administrator.objects.get(pk=val)

            if admin.type == 1:
                websites = Websites.objects.all()
                websitesName = []

                for items in websites:
                    websitesName.append(items.domain)
            else:
                if admin.type == 2:
                    websites = admin.websites_set.all()
                    admins = Administrator.objects.filter(owner=admin.pk)
                    websitesName = []

                    for items in websites:
                        websitesName.append(items.domain)

                    for items in admins:
                        webs = items.websites_set.all()

                        for web in webs:
                            websitesName.append(web.domain)


                else:
                    websitesName = []
                    websites = Websites.objects.filter(admin=admin)
                    for items in websites:
                        websitesName.append(items.domain)

            return render(request, 'mailServer/dkimManager.html',
                          {'websiteList': websitesName, 'openDKIMInstalled': openDKIMInstalled})

        return render(request, 'mailServer/dkimManager.html',
                      {'openDKIMInstalled': openDKIMInstalled})



    except KeyError:
        return redirect(loadLoginPage)


def fetchDKIMKeys(request):
    try:
        val = request.session['userID']
        try:
            if request.method == 'POST':
                data = json.loads(request.body)

                domainName = data['domainName']

                try:
                    path = "/etc/opendkim/keys/" + domainName + "/default.txt"
                    command = "sudo cat " + path
                    output = subprocess.check_output(shlex.split(command))

                    path = "/etc/opendkim/keys/" + domainName + "/default.private"
                    command = "sudo cat " + path
                    privateKey = subprocess.check_output(shlex.split(command))

                    data_ret = {'fetchStatus': 1, 'keysAvailable': 1, 'publicKey': output[53:269],
                                'privateKey': privateKey, 'dkimSuccessMessage': 'Keys successfully fetched!', 'error_message': "None"}
                    json_data = json.dumps(data_ret)
                    return HttpResponse(json_data)

                except BaseException,msg:
                    data_ret = {'fetchStatus': 1, 'keysAvailable': 0, 'error_message': str(msg)}
                    json_data = json.dumps(data_ret)
                    return HttpResponse(json_data)


        except BaseException,msg:
            data_ret = {'fetchStatus': 0, 'error_message': str(msg)}
            json_data = json.dumps(data_ret)
            return HttpResponse(json_data)
    except KeyError,msg:
        data_ret = {'fetchStatus': 0, 'error_message': str(msg)}
        json_data = json.dumps(data_ret)
        return HttpResponse(json_data)


def generateDKIMKeys(request):
    try:
        val = request.session['userID']
        try:
            if request.method == 'POST':

                data = json.loads(request.body)

                domainName = data['domainName']

                execPath = "sudo python " + virtualHostUtilities.cyberPanel + "/plogical/mailUtilities.py"

                execPath = execPath + " generateKeys --domain " + domainName

                output = subprocess.check_output(shlex.split(execPath))

                if output.find("1,None") > -1:

                    zone = dnsDomains.objects.get(name=domainName)
                    zone.save()

                    path = "/etc/opendkim/keys/" + domainName + "/default.txt"
                    command = "sudo cat " + path
                    output = subprocess.check_output(shlex.split(command))

                    record = dnsRecords(domainOwner=zone,
                                     domain_id=zone.id,
                                     name="default._domainkey." + domainName,
                                     type="TXT",
                                     content="v=DKIM1; k=rsa; p=" + output[53:269],
                                     ttl=3600,
                                     prio=0,
                                     disabled=0,
                                     auth=1)
                    record.save()

                    data_ret = {'generateStatus': 1, 'error_message': "None"}
                    json_data = json.dumps(data_ret)
                    return HttpResponse(json_data)

                else:
                    data_ret = {'generateStatus': 0, 'error_message': output}
                    json_data = json.dumps(data_ret)
                    return HttpResponse(json_data)

        except BaseException,msg:
            data_ret = {'generateStatus': 0, 'error_message': str(msg)}
            json_data = json.dumps(data_ret)
            return HttpResponse(json_data)
    except BaseException, msg:
        data_ret = {'generateStatus': 0, 'error_message': str(msg)}
        json_data = json.dumps(data_ret)
        return HttpResponse(json_data)

def installOpenDKIM(request):
    try:
        val = request.session['userID']
        try:
            thread.start_new_thread(mailUtilities.installOpenDKIM, ('Install','openDKIM'))
            final_json = json.dumps({'installOpenDKIM': 1, 'error_message': "None"})
            return HttpResponse(final_json)
        except BaseException,msg:
            final_dic = {'installOpenDKIM': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)
    except KeyError:
        final_dic = {'installOpenDKIM': 0, 'error_message': "Not Logged In, please refresh the page or login again."}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)

def installStatusOpenDKIM(request):
    try:
        val = request.session['userID']
        try:
            if request.method == 'POST':

                command = "sudo cat " + mailUtilities.installLogPath
                installStatus = subprocess.check_output(shlex.split(command))

                if installStatus.find("[200]")>-1:

                    execPath = "sudo python " + virtualHostUtilities.cyberPanel + "/plogical/mailUtilities.py"

                    execPath = execPath + " configureOpenDKIM"

                    output = subprocess.check_output(shlex.split(execPath))

                    if output.find("1,None") > -1:
                        pass
                    else:
                        final_json = json.dumps({
                            'error_message': "Failed to install OpenDKIM configurations.",
                            'requestStatus': installStatus,
                            'abort': 1,
                            'installed': 0,
                        })
                        return HttpResponse(final_json)

                    final_json = json.dumps({
                                             'error_message': "None",
                                             'requestStatus': installStatus,
                                             'abort':1,
                                             'installed': 1,
                                             })
                    return HttpResponse(final_json)
                elif installStatus.find("[404]") > -1:

                    final_json = json.dumps({
                                             'abort':1,
                                             'installed':0,
                                             'error_message': "None",
                                             'requestStatus': installStatus,
                                             })
                    return HttpResponse(final_json)

                else:
                    final_json = json.dumps({
                                             'abort':0,
                                             'error_message': "None",
                                             'requestStatus': installStatus,
                                             })
                    return HttpResponse(final_json)


        except BaseException,msg:
            final_dic = {'abort':1,'installed':0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)
    except KeyError:
        final_dic = {'abort':1,'installed':0, 'error_message': "Not Logged In, please refresh the page or login again."}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)

