from django.http import HttpResponse
from webrtc.P2SRTCPeer import P2SRTCPeer
from webrtc.S2SRTCPeer import S2SRTCPeer
from aiortc.contrib.media import MediaBlackhole
import uuid
from base import views as base_views
from asgiref.sync import sync_to_async
from base.models import CUser
class Pairing:
    p2sTrack = 0
    def __init__(self, s2sOffer, username, nTracks=1) -> None:
        self.s2sOffer = s2sOffer
        self.pcon = P2SRTCPeer()
        self.scon = S2SRTCPeer()
        self.uuid = uuid.uuid4()
        self.nTracks = nTracks
        self.username = username
        self.blackhole = MediaBlackhole()

    async def eatMedia(self):
        for v in self.tracks:
            self.blackhole.addTrack(v)
        await self.blackhole.start()

    async def closeEvent(self):
        del self.pcon
        self.pcon = P2SRTCPeer()
        await self.eatMedia()

    async def connectP2S(self, P2Srequest):
        del self.pcon
        self.pcon = P2SRTCPeer()
        self.p2sTrack = P2Srequest["track"]
        video = self.tracks[self.p2sTrack]
        self.res = await self.pcon.handle(
            request=P2Srequest,
            video = (video),
            closeEvent=self.closeEvent,
        )
        self.free = False
        return self.res
    def changeP2SModels(self, models):
        self.pcon.changeP2SModels(models)

    async def closeS2S(self, username):
        await base_views.deactivateTracksForUser(username=username)
    async def connectS2S(self):
        del self.scon
        self.scon = S2SRTCPeer()
        # await base_views.deactivateTracksForUser(username=self.username)
        res = await self.scon.handle(offer=self.s2sOffer, nTracks= self.nTracks, uuid=self.uuid, closeCallback=self.closeS2S, username=self.username)
        self.tracks = self.scon.getS()
        await self.eatMedia()
        return res