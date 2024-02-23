import asyncio
import json
from av import VideoFrame
import logging
import time
import os
from django.http import HttpResponse
from django.shortcuts import render
import json
from webrtc import customVideoTrack
import uuid
from aiortc import (
    MediaStreamTrack,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)
from aiortc.contrib.media import MediaRelay
from webrtc.P2SRTCPeer import P2SRTCPeer
from webrtc.S2SRTCPeer import S2SRTCPeer
from django.views.decorators.csrf import csrf_exempt
from webrtc.Pairing import Pairing
from asgiref.sync import sync_to_async

from django.contrib.auth.hashers import make_password, check_password
from base.models import CUser
from base.views import isAuthenticated, setTracksForUser

ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")
pc = RTCPeerConnection()

con = []

async def p2sHttpIndex(request):
    return render(request, "./p2sHttp.html")


@csrf_exempt
async def p2sOffer(request):
    body = request.body
    parsedReq = json.loads(body)
    username = parsedReq["username"]
    password = parsedReq["password"]
    offer = parsedReq["offer"]
    cond = await sync_to_async(isAuthenticated)(username, password)
    if cond:
        if len(con) != 0:
            for pairing in con:
                user = await sync_to_async(CUser.objects.get)(username=username)
                if str(user.streamID) == str(pairing["pairing"].uuid):
                    res = await pairing["pairing"].connectP2S(P2Srequest=offer)
                    return HttpResponse(res)
            else:
                return HttpResponse("no stream for this user")
        return HttpResponse("no S2S connection")
    return HttpResponse("user not authenticated")

@csrf_exempt
async def changeP2SModel(request):
    body = request.body
    parsedReq = json.loads(body)
    username = parsedReq["username"]
    models = parsedReq["model"]
    if len(con) != 0:
        for pairing in con:
            user = await sync_to_async(CUser.objects.get)(username=username)
            if str(user.streamID) == str(pairing["pairing"].uuid):
                pairing["pairing"].changeP2SModels(models)
                return HttpResponse("model changed to", models)
        else:
            return HttpResponse("no stream for this user")
    return HttpResponse("no S2S connection")


@csrf_exempt
async def s2sOffer(request):
    parsedReq = json.loads(request.body)
    username = parsedReq["username"]
    password = parsedReq["password"]
    nTracks = parsedReq["nTracks"]
    cond = await sync_to_async(isAuthenticated)(username, password)
    if cond:
        offerJson = json.loads(parsedReq["offer"])
        streamNames = parsedReq["streamNames"]
        trackNames = streamNames
        await sync_to_async(setTracksForUser)(trackNames, username)
        offer = RTCSessionDescription(**offerJson)
        i = Pairing(s2sOffer=offer,username=username, nTracks = nTracks)
        await sync_to_async(CUser.objects.filter(username=username).update)(
            streamID=i.uuid
        )
        con.append({"id": i.uuid, "pairing": i})
        res = await con[-1]["pairing"].connectS2S()
        return res
    else:
        return HttpResponse("authentication failed")