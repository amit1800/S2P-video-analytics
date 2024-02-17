from django.contrib.auth.hashers import check_password
from base.models import CUser
from rest_framework.response import Response
import json

def isAuthenticated(username, password):
    if username is None or password is None or username == "" or password == "":
        return False
    try:
        if len(CUser.objects.all().filter(username=username))>0:
            if check_password(password, CUser.objects.get(username=username).password):
                print("****************USER EXISTS*********************")
                return True
            else:
                print("****************WRONG PASSWORD*********************")
                return False
        else:
            print("****************USER DOES NOT EXISTS*********************")
            return False
    except:
        print("****************something wrong*****************")
        return False

def getStreams(username):
    return CUser.objects.get(username=username).streamID

def createNewUser(firstname, lastname, username, password):
    print(firstname, lastname,username, password)
    try:
        user = CUser()
        user.firstName = firstname
        user.lastName = lastname
        user.username = username
        user.password = password
        user.save()
        return Response({"status": True, "username" : username, "subscription": 1 })
    except:
        return Response({"status": False})
    
def getStreamNamesFromModel(username):
    userStreamNames = CUser.objects.all().filter(username=username)[0].streamNames
    # print(json.loads(userStreamNames))
    print("userStreams",userStreamNames)
    print(json.loads(userStreamNames)[0])
    d = {v: k for v, k in enumerate(json.loads(userStreamNames))}
    print(d)
    d2 = {0:"amit", 1:'amar'}
    return Response({"streamNames": d})

def setStreamNamesToModel(username, streamNames):
    user = CUser.objects.all().filter(username=username)
    print(user[0].streamNames)
    user.update(streamNames = streamNames)
