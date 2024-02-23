import json
import time
from django.http import HttpResponse
import json
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from webrtc.ProcessTrack import ProcessTrack
from base import views as base_views
from asgiref.sync import sync_to_async
import asyncio
from concurrent.futures import ThreadPoolExecutor

class P2SRTCPeer:
    relay = MediaRelay()
    def __init__(self) -> None:
        self.overlay = ProcessTrack()
        ice_server = RTCIceServer(urls=["stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"])
        self.configuration = RTCConfiguration(iceServers=[ice_server])
        self.pc = RTCPeerConnection(configuration=self.configuration)
        self.dataChannel = self.pc.createDataChannel("s2pdc")
        self.blackhole = MediaBlackhole()

    def changeP2SModels(self, models):
        self.overlay.changeModels(models)

    async def handle(self, request, video, closeEvent):
        self.dataChannel.close()
        del self.pc
        self.pc = RTCPeerConnection(configuration=self.configuration)
        self.params = request
        self.video = video
        offer = RTCSessionDescription(sdp=self.params["sdp"], type=self.params["type"])
        self.dataChannel = self.pc.createDataChannel("s2pdc")
        def evt_callback(type, message):
            #insert evt in database

            asyncio.create_task(base_views.addDetection(type, message))
            self.dataChannel.send(json.dumps({"type":type,"message": message}))
        
        transceiver = self.pc.addTransceiver(trackOrKind="video", direction="sendrecv")

        self.overlay.initialize(self.video, evt_callback, self.params["model"])

        local_track = self.overlay
        transceiver.sender.replaceTrack(local_track)
        @self.dataChannel.on("open")
        def on_open():
            print("peer data channel established",self)
        @self.dataChannel.on("close")
        async def on_close():
            print("peer data channel closed", self)
            await closeEvent()
        await self.pc.setRemoteDescription(offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        return HttpResponse(
            json.dumps(
                {"sdp": self.pc.localDescription.sdp, "type": self.pc.localDescription.type}
            ),
        )
