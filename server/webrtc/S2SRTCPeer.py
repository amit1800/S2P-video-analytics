import asyncio
import json
from django.http import HttpResponse
import json
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaBlackhole

class S2SRTCPeer:
    def __init__(self) -> None:
        self.video = []
        self.blackhole = MediaBlackhole()

    def getS(self):
        if self.video:
            return self.video
        else:
            return None

    def object_to_string(self, obj):
        try:
            if isinstance(obj, RTCSessionDescription):
                message = {"sdp": obj.sdp, "type": obj.type}
            return json.dumps(message, sort_keys=True)
        except:
            return "error"
        
    async def handle(self, offer, nTracks, uuid, closeCallback, username):
        self.nTracks = nTracks
        self.uuid = uuid
        pc = RTCPeerConnection()
        transceiver = pc.addTransceiver(trackOrKind="video", direction="recvonly")
        transceiver.direction = "recvonly"
        obj = offer
        self.lastBeat = 0
        self.idle = False
        async def check_heartbeat():
            while self.idle:
                diff = asyncio.get_event_loop().time() - self.lastBeat
                if diff > 2:
                    self.idle = False
                    await closeCallback(username)
                await asyncio.sleep(1)
        @pc.on("datachannel")
        async def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                if not message=="message":
                    print(message)
                if not self.idle:
                    asyncio.create_task(check_heartbeat())
                self.idle = True
                self.lastBeat = asyncio.get_event_loop().time()
        @pc.on("track")
        async def on_track(remoteSteamTrack):
            self.video.append((remoteSteamTrack))
            print("recieved video track", remoteSteamTrack.id)
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            await pc.setLocalDescription(await pc.createAnswer())
            return HttpResponse(self.object_to_string(pc.localDescription))
        else:
            print(obj)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, input)
        return HttpResponse(json.loads('{"msg":"helo"}'))