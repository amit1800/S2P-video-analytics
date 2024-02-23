import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import asyncio
import random
from numpy import ndarray


face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

class ProcessTrack(VideoStreamTrack):

    def __init__(self) -> None:
        self.mappings = {
            "Human": self.modelHuman,
            "Fire": self.modelFire,
            "Weapon" :self.modelWeapon,
            "NumberPlate": self.modelNumberPlate
        }
        super().__init__()

    def initialize(self, track, alertCallback, model=["Number Plate"]):

        self.mappings = {
            "Human": self.modelHuman,
            "Fire": self.modelFire,
            "Weapon" :self.modelWeapon,
            "NumberPlate": self.modelNumberPlate
        }
        self.track = track
        # self.model = self.mappings[model]
        # model = ["Number Plate"]
        self.changeModels(model)
        self.alertCallback = alertCallback

    def changeModel(self, model):
        self.model = self.mappings[model]
    
    def changeModels(self, models):
        if not all(model in self.mappings for model in models):
            raise ValueError("Invalid model(s) provided.")
        pipeline = [self.mappings[model] for model in models]
        self.model = lambda x: self.modelPipe(x, pipeline)

    def modelPipe(self,image, pipeline):
        result = image
        for func in pipeline:
            result = func(result)
        return result

    
    
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
        return (image)
    
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
        return (image)
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
        return (image)
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
        return (image)
        
        
    async def recv(self):
        def detect_faces(img):
            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # return gray
            # Detect faces in the image
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return img
            # Draw rectangles around the faces
            for x, y, w, h in faces:
                img2 = cv2.rectangle(
                    img,
                    (x, y),
                    (x + w, y + h),
                    (255, 0, 0),
                    2,
                )
                # return img2
            return img2
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        new_frame = VideoFrame.from_ndarray((self.model(img)), format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame
