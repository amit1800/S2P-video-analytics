import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame

from modules import TRTModule
from modules.utils import blob, letterbox, det_postprocess

import random
from numpy import ndarray
import torch
import asyncio

from from_root import from_root

random.seed(0)

# # detection model classes
# CLASSES = ('human', 'smoke', 'fire', 'numbers' ,'knife','pistol')
# # colors for per classes
# COLORS = {
#     cls: [random.randint(0, 255) for _ in range(3)]
#     for i, cls in enumerate(CLASSES)
# }

# Model 1: Human detection
CLASSES1 = ('human',)
COLORS1 = {
    'human':(0,0,0)
}

# Model 2: Smoke and Fire detection
CLASSES2 = ('smoke', 'fire')
COLORS2 = {
    'smoke':(1,2,3),
    'fire' :(5,5,5)
}

# Model 3: Number plate detection
CLASSES3 = ('number-plate',)
COLORS3 = {
    'number-plate':(10,10,10)
}

# Model 4: Knife and Pistol detection
CLASSES4 = ('knife', 'pistol')
COLORS4 = {
    'knife':(20,20,20),
    'pistol':(30,30,30)
}

# # Load Engine file 
# engine_file = '/home/ubuntu/S2PS/weights/best-human.engine'
# device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# engine = TRTModule(engine_file, device)
# H, W = engine.inp_info[0].shape[-2:]
# # set desired output names order
# engine.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

# Load Engine file 1
engine_file1 = '/home/ubuntu/S2PS/weights/best-human.engine'
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
engine1 = TRTModule(engine_file1, device)
H, W = engine1.inp_info[0].shape[-2:]
# set desired output names order
engine1.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

# Load Engine file 2 
engine_file2 = '/home/ubuntu/S2PS/weights/best-fire.engine'
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
engine2 = TRTModule(engine_file2, device)
H, W = engine2.inp_info[0].shape[-2:]
# set desired output names order
engine2.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

# Load Engine file 3
engine_file3 = '/home/ubuntu/S2PS/weights/best-numplate.engine'
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
engine3 = TRTModule(engine_file3, device)
H, W = engine3.inp_info[0].shape[-2:]
# set desired output names order
engine3.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

# Load Engine file 4
engine_file4 = '/home/ubuntu/S2PS/weights/best-weapon.engine'
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
engine4 = TRTModule(engine_file4, device)
H, W = engine4.inp_info[0].shape[-2:]
# set desired output names order
engine4.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])


# function for model

# def detect(input_frame:ndarray) -> ndarray:
#     draw = input_frame.copy()
#     bgr, ratio, dwdh = letterbox(input_frame, (W, H))
#     rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
#     tensor = blob(rgb, return_seg=False)
#     dwdh = torch.asarray(dwdh * 2, dtype=torch.float32, device=device)
#     tensor = torch.asarray(tensor, device=device)
#     # inference
#     data = engine(tensor)
#     bboxes, scores, labels = det_postprocess(data)
#     if bboxes.numel() == 0:
#         # if no bounding box
#         print('No object!')
    
#         return input_frame
#     bboxes -= dwdh
#     bboxes /= ratio

#     for (bbox, score, label) in zip(bboxes, scores, labels):
#         bbox = bbox.round().int().tolist()
#         blob_1 = draw[bbox[0]:bbox[2], bbox[1]: bbox[3], :]
#         cls_id = int(label)
#         cls = CLASSES[cls_id]
#         color = COLORS[cls]
#         cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
#         cv2.putText(draw,
#                     f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.75, [225, 255, 255],
#                     thickness=2)
#     return draw

# function for 1st model

def detect1(input_frame:ndarray) -> ndarray:
    draw = input_frame.copy()
    bgr, ratio, dwdh = letterbox(input_frame, (W, H))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    tensor = blob(rgb, return_seg=False)
    dwdh = torch.asarray(dwdh * 2, dtype=torch.float32, device=device)
    tensor = torch.asarray(tensor, device=device)
    # inference
    data = engine1(tensor)
    bboxes, scores, labels = det_postprocess(data)
    if bboxes.numel() == 0:
        # if no bounding box
        print('No object!')
    
        return input_frame
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        blob_1 = draw[bbox[0]:bbox[2], bbox[1]: bbox[3], :]
        cls_id = int(label)
        cls = CLASSES1[cls_id]
        color = COLORS1[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, [225, 255, 255],
                    thickness=2)
    return draw

#function for 2nd model

def detect2(input_frame:ndarray) -> ndarray:
    draw = input_frame.copy()
    bgr, ratio, dwdh = letterbox(input_frame, (W, H))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    tensor = blob(rgb, return_seg=False)
    dwdh = torch.asarray(dwdh * 2, dtype=torch.float32, device=device)
    tensor = torch.asarray(tensor, device=device)
    # inference
    data = engine2(tensor)
    bboxes, scores, labels = det_postprocess(data)
    if bboxes.numel() == 0:
        # if no bounding box
        print('No object!')
    
        return input_frame
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        blob_1 = draw[bbox[0]:bbox[2], bbox[1]: bbox[3], :]
        cls_id = int(label)
        cls = CLASSES2[cls_id]
        color = COLORS2[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, [225, 255, 255],
                    thickness=2)
    return draw

# function for 3rd model

def detect3(input_frame:ndarray) -> ndarray:
    draw = input_frame.copy()
    bgr, ratio, dwdh = letterbox(input_frame, (W, H))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    tensor = blob(rgb, return_seg=False)
    dwdh = torch.asarray(dwdh * 2, dtype=torch.float32, device=device)
    tensor = torch.asarray(tensor, device=device)
    # inference
    data = engine3(tensor)
    bboxes, scores, labels = det_postprocess(data)
    if bboxes.numel() == 0:
        # if no bounding box
        print('No object!')
    
        return input_frame
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        blob_1 = draw[bbox[0]:bbox[2], bbox[1]: bbox[3], :]
        cls_id = int(label)
        cls = CLASSES3[cls_id]
        color = COLORS3[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, [225, 255, 255],
                    thickness=2)
    return draw

# function for 4th model

def detect4(input_frame:ndarray) -> ndarray:
    draw = input_frame.copy()
    bgr, ratio, dwdh = letterbox(input_frame, (W, H))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    tensor = blob(rgb, return_seg=False)
    dwdh = torch.asarray(dwdh * 2, dtype=torch.float32, device=device)
    tensor = torch.asarray(tensor, device=device)
    # inference
    data = engine4(tensor)
    bboxes, scores, labels = det_postprocess(data)
    if bboxes.numel() == 0:
        # if no bounding box
        print('No object!')
    
        return input_frame
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        blob_1 = draw[bbox[0]:bbox[2], bbox[1]: bbox[3], :]
        cls_id = int(label)
        cls = CLASSES4[cls_id]
        color = COLORS4[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, [225, 255, 255],
                    thickness=2)
    return draw

class Overlay(VideoStreamTrack):
    def __init__(self, track) -> None:
        self.track = track
        super().__init__()

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        r1 = img
        try:
            r4 = detect4(img)
            r3 = detect3(r4)
            r2 = detect2(r3)
            r1 = detect1(r2)
            print("Recieved Result")
        except Exception as e:
            print("Error Occured!!! Sending empty frame" , e)
        new_frame = VideoFrame.from_ndarray(r1, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame
