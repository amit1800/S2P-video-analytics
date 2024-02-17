from django.http import HttpResponse
from webrtc.P2SRTCPeer import P2SRTCPeer
from webrtc.S2SRTCPeer import S2SRTCPeer
from aiortc.contrib.media import MediaRelay, MediaBlackhole
from webrtc.ProcessTrack import ProcessTrack
import uuid
from asgiref.sync import async_to_sync
import asyncio

class Pairing:
    id = 0
    free = True
    p2sTrack = 0
    # relay = MediaRelay()
    def __init__(self, s2sOffer, id=id, nTracks=1) -> None:
        self.s2sOffer = s2sOffer
        self.pcon = P2SRTCPeer()
        self.scon = S2SRTCPeer()
        self.id = id
        self.uuid = uuid.uuid4()
        self.nTracks = nTracks

        self.blackhole = MediaBlackhole()

    async def eatMedia(self):
        print("BLACK HOLE ACTIVATED")
        for v in self.video:
            self.blackhole.addTrack(v)
        await self.blackhole.start()
    async def closeEvent(self):
        self.free = True
        del self.pcon
        self.pcon = P2SRTCPeer()
        print("peer closed, so pairing is open. free:", self.free)
        await self.eatMedia()
        # del self.pcon
        # self.pcon = P2SRTCPeer()

    async def connectP2S(self, P2Srequest):
        del self.pcon
        self.pcon = P2SRTCPeer()
        self.p2sTrack = P2Srequest["framerate"]
        print("Peer requested for this track: ", self.p2sTrack)
        video = self.video[self.p2sTrack]
        self.res = await self.pcon.handle(
            request=P2Srequest,
            # video=self.relay.subscribe(track=self.video[1]),
            video = (video),
            closeEvent=self.closeEvent,
        )
        # self.pcon.changeP2SModel()
        self.free = False
        return self.res
        if self.free:
            pass
        else:
            return HttpResponse("not available")
    def changeP2SModels(self, models):
        self.pcon.changeP2SModels(models)
    async def connectS2S(self):
        del self.scon
        self.scon = S2SRTCPeer()
        res = await self.scon.handle(offer=self.s2sOffer, nTracks= self.nTracks, uuid=self.uuid,)
        self.video = self.scon.getS()
        await self.eatMedia()
        return res