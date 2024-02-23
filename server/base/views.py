from django.contrib.auth.hashers import check_password
from base.models import CUser, Track, Detection
from rest_framework.response import Response
import json
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

import asyncio
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
    
def setTracksForUser(tracks, username):
    tracks = json.loads(tracks)
    cuser = CUser.objects.all().filter(username=username)[0]
    cuser_tracks = cuser.track_set.all()
    cuser_tracks.update(active = False)
    for i in tracks:
        track = Track()
        track.name = i
        track.cuser = cuser
        track.active = True
        track.save()

def getAcitveTracksForUser(username):
    cuser_tracks = CUser.objects.all().filter(username=username)[0].track_set.all().filter(active=True)
    tracks = []
    for q in cuser_tracks:
        tracks.append(q.name)
    d = {v: k for v, k in enumerate(tracks)}
    return Response({"streamNames": d})

async def deactivateTracksForUser(username):
    cuser = await sync_to_async(CUser.objects.get)(username=username)
    tracks_query = cuser.track_set.filter(active=True)
    await sync_to_async(tracks_query.update)(active = False)

async def addDetection(type, value):
    print(type, value)
    try:
        detection = Detection()
        detection.type = type
        detection.value = value
        await database_sync_to_async(detection.save)()
    except Exception as e: print(e)