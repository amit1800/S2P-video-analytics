import asyncio
import json
from av import VideoFrame
import logging
import time
from asgiref.sync import async_to_sync

# import cv2
import os
from django.http import HttpResponse


from django.shortcuts import render
import json

from webrtc import customVideoTrack
from aiortc import (
    MediaStreamTrack,
    RTCPeerConnection,
    RTCSessionDescription,
    RTCConfiguration,
    RTCIceServer,
)
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from webrtc.ProcessTrack import ProcessTrack
from webrtc.Overlay import Overlay
class P2SRTCPeer:
    relay = MediaRelay()
    def __init__(self) -> None:
        self.overlay = ProcessTrack()
        ice_server = RTCIceServer(
            urls=["stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"]
        )
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
        # self.onClose = function
        self.video = video
        offer = RTCSessionDescription(sdp=self.params["sdp"], type=self.params["type"])
        self.dataChannel = self.pc.createDataChannel("s2pdc")
        def sendAlert(type, message):
            self.dataChannel.send(json.dumps({"type":type,"message": message}))
        transceiver = self.pc.addTransceiver(trackOrKind="video", direction="sendrecv")
        # local_video = customVideoTrack.CustomVideoTrack(self.params["framerate"])
        self.overlay.initialize(self.video, sendAlert, self.params["model"])
        local_track = self.overlay
        # Overlay(self.video)
        transceiver.sender.replaceTrack(local_track)

        @self.dataChannel.on("open")
        def on_open():
            print("peer data channel established",self)
            sendAlert("alert", "test")

        @self.dataChannel.on("close")
        async def on_close():
            print("peer data channel closed", self)
            # del self.pc
            # self.__init__()
            await closeEvent()


        @self.pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            if self.pc.iceConnectionState == "failed":
                # self.onClose(self)
                # print("connection failed")
                pass

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            # channel.close()
            # to send periodic pings
            # async def send_pings():
            #     while True:
            #         msg = "ping"
            #         channel.send(msg)
            #         await asyncio.sleep(1)

            # asyncio.ensure_future(send_pings())

            # print("data channel opened")
            channel.send("data channel opened")

            @channel.on("message")
            def on_message(m):
                # print("data channel: " + m)
                pass

            @channel.on("close")
            def on_close():
                # print("peer data channel closed")
                
                self.pc.close()

        @self.pc.on("track")
        def on_track(track):
            pass
            # pc.addTrack(track)
            # local_video = rtspOut("rtsp://192.168.214.72:1935")
            # local_video = rtspOut(track)
            # local_video = pureRtspOut(useDefaultFrameRate=False, framerate=15)
            # local_video = customVideoTrack.CustomVideoTrack(1)
            # pc.addTrack(local_video)
        # dc.send("working")

        # handle offer
        await self.pc.setRemoteDescription(offer)

        # send answer
        answer = await self.pc.createAnswer()
        start_time = time.time()
        await self.pc.setLocalDescription(answer)
        print("--- %s seconds ---" % (time.time() - start_time))

        return HttpResponse(
            json.dumps(
                {"sdp": self.pc.localDescription.sdp, "type": self.pc.localDescription.type}
            ),
        )
