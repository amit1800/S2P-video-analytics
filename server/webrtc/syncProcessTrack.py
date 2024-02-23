import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import asyncio
import random
from numpy import ndarray

AWS_FLAG = False

if AWS_FLAG:
    from modules import TRTModule
    from modules.utils import blob, letterbox, det_postprocess, keras_detector
    import torch

random.seed(0)

# # detection model classes
# CLASSES = ('human', 'smoke', 'fire', 'numbers' ,'knife','pistol')
# # colors for per classes
# COLORS = {
#     cls: [random.randint(0, 255) for _ in range(3)]
#     for i, cls in enumerate(CLASSES)
# }

# Model 1: Human detection
CLASSES1 = ('human')
COLORS1 = {
    'human':(127,0,255)
}

# Model 2: Smoke and Fire detection
CLASSES2 = ('smoke', 'fire')
COLORS2 = {
    'smoke':(51,0,0),
    'fire' :(102,0,102)
}

# Model 3: Number plate detection
CLASSES3 = ('number-plate',)
COLORS3 = {
    'number-plate':(0,204,204)
}

# Model 4: Knife and Pistol detection
CLASSES4 = ('knife', 'pistol')
COLORS4 = {
    'knife':(153,0,153),
    'pistol':(51,0,51)
}

# # Load Engine file 
# engine_file = '/home/ubuntu/S2PS/weights/best-human.engine'
# device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# engine = TRTModule(engine_file, device)
# H, W = engine.inp_info[0].shape[-2:]
# # set desired output names order
# engine.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

# Load Engine file 1
if AWS_FLAG:
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    engine_file1 = '/home/ubuntu/S2PS/weights/best-human.engine'
    engine1 = TRTModule(engine_file1, device)
    H, W = engine1.inp_info[0].shape[-2:]
    # set desired output names order
    engine1.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

    # Load Engine file 2 
    engine_file2 = '/home/ubuntu/S2PS/weights/best-fire.engine'
    engine2 = TRTModule(engine_file2, device)
    H, W = engine2.inp_info[0].shape[-2:]
    # set desired output names order
    engine2.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

    # Load Engine file 3
    engine_file3 = '/home/ubuntu/S2PS/weights/best-numplate.engine'
    engine3 = TRTModule(engine_file3, device)
    H, W = engine3.inp_info[0].shape[-2:]
    # set desired output names order
    engine3.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

    # Load Engine file 4
    engine_file4 = '/home/ubuntu/S2PS/weights/best-weapon.engine'
    engine4 = TRTModule(engine_file4, device)
    H, W = engine4.inp_info[0].shape[-2:]
    # set desired output names order
    engine4.set_desired(['num_dets', 'bboxes', 'scores', 'labels'])

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def HumanModel(input_frame:ndarray, callback) -> ndarray:
    draw = input_frame.copy()
    cv2.circle(draw, (200, 100), 20, COLORS1['human'], -1)
    if  not AWS_FLAG:
        if random.randint(0,15) == 0:
            callback("human", "Human Detected")
        return draw
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
        return draw
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        cls_id = int(label)
        if cls_id == 0:
            cls = CLASSES1[cls_id]
            color = COLORS1[cls]
            cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
            cv2.putText(draw,
                        f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, color,
                        thickness=2)
    callback("human", "Human Detected")
    return draw


def FireModel(input_frame:ndarray, callback) -> ndarray:
    draw = input_frame.copy()
    cv2.circle(draw, (250, 100), 20, COLORS2['fire'], -1)
    if not AWS_FLAG:
        if random.randint(0,15) == 0:
            callback("fire", "Fire Detected")
        return draw
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
        return draw
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        cls_id = int(label)
        cls = CLASSES3[cls_id]
        color = COLORS3[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, color,
                    thickness=2)
    callback("fire", "Fire Detected")
    return draw





def WeaponModel(input_frame:ndarray, callback) -> ndarray:
    draw = input_frame.copy()
    cv2.circle(draw, (300, 100), 20, COLORS4['knife'], -1)
    if not AWS_FLAG:
        if random.randint(0,15) == 0:
            callback("weapon", "Weapon Detected")
        return draw
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
    
        return draw
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        cls_id = int(label)
        cls = CLASSES4[cls_id]
        color = COLORS4[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, color,
                    thickness=2)
    callback("weapon", "Weapon Detected")
    return draw
def NumberPlateModel(input_frame:ndarray, callback) -> ndarray:
    draw = input_frame.copy()
    cv2.circle(draw, (350, 100), 20, COLORS3['number-plate'], -1)
    if not AWS_FLAG:
        if random.randint(0,15) == 0:
            callback("numberplate", "Number Plate")
        return draw
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
    
        return draw
    bboxes -= dwdh
    bboxes /= ratio

    for (bbox, score, label) in zip(bboxes, scores, labels):
        bbox = bbox.round().int().tolist()
        blob_1 = draw[bbox[1]:bbox[3], bbox[0]: bbox[2], :]
        licence_plate_num = keras_detector(blob_1)
        callback("numberplate", licence_plate_num)
        cls_id = int(label)
        cls = CLASSES3[cls_id]
        color = COLORS3[cls]
        cv2.rectangle(draw, bbox[:2], bbox[2:], color, 2)
        cv2.putText(draw,
                    f'{cls}:{score:.3f}', (bbox[0], bbox[1] - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, color,
                    thickness=2)
    return draw



class ProcessTrack(VideoStreamTrack):

    def __init__(self) -> None:
        self.mappings = {
            "Human": HumanModel,
            "Fire": FireModel,
            "Weapon" :WeaponModel,
            "NumberPlate": NumberPlateModel
        }
        super().__init__()

    def initialize(self, track, alertCallback, model=["NumberPlate"]):
        # self.mappings = {
        #     "Human": self.modelHuman,
        #     "Fire": self.modelFire,
        #     "Weapon" :self.modelWeapon,
        #     "NumberPlate": self.modelNumberPlate
        # }
        self.track = track
        # self.model = self.mappings[model]
        # model = ["NumberPlate"]
        self.changeModels(model)
        self.alertCallback = alertCallback

    def changeModel(self, model):
        self.model = self.mappings[model]
    
    def changeModels(self, models):
        if not all(model in self.mappings for model in models):
            raise ValueError("Invalid model(s) provided.")
        pipeline = [self.mappings[model] for model in models]

        self.model =  lambda x: self.modelPipe(x, pipeline)

    def modelPipe(self,image, pipeline):
        result = image
        for func in pipeline:
            result = func(result, self.alertCallback)
        return result

    
    '''
    def modelHuman(self,image):
        text = "Human"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (255, 255, 255) 
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (image.shape[1] - text_size[0]) // 4
        text_y = (image.shape[0] + text_size[1]) // 2
        cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)
        return humanModel(image)
    
    def modelFire(self,image):
        text = "Fire"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (255,255, 0) 
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (image.shape[1] - text_size[0]) // 4
        text_y = (image.shape[0] + text_size[1]) // 4

        if random.randint(0,20) == 1:
            self.alertCallback("fire", "test")
        cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)
        return NumberPlateModel(image, self.alertCallback)
    def modelWeapon(self,image):
        text = "Weapon"
        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        font_scale = 3
        font_color = (255, 255, 255) 
        thickness = 1
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (image.shape[1] - text_size[0]) // 2
        text_y = (image.shape[0] + text_size[1]) // 2
        cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)
        return WeaponModel(image)
    def modelNumberPlate(self,image):
        text = "Number Plate"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (0, 0, 0) 
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (image.shape[1] - text_size[0]) // 2
        text_y = (image.shape[0] + text_size[1]) // 2
        #stupid code, don't forget to remove
        if random.randint(0,20) == 1:
            self.alertCallback("numberplate", "MH20 DP 5754")
        cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)
        return FireModel(image)'''
        
        
    async def recv(self):
        # def detect_faces(img):
        #     # Convert the image to grayscale
        #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #     # return gray
        #     # Detect faces in the image
        #     faces = face_cascade.detectMultiScale(
        #         gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        #     )
            
        #     if len(faces) == 0:
        #         return img
        #     # Draw rectangles around the faces
        #     for x, y, w, h in faces:
        #         img2 = cv2.rectangle(
        #             img,
        #             (x, y),
        #             (x + w, y + h),
        #             (255, 0, 0),
        #             2,
        #         )
        #         # return img2
        #     return img2
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        try:
        
            new_frame = VideoFrame.from_ndarray((self.model(img)), format="bgr24")
        except Exception as e: print(e)
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame