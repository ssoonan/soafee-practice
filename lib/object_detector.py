from typing import List

import cv2
from ultralytics import YOLO
# from ultralytics.utils.plotting import Annotator, colors

class ObjectDetector:
    """Runs YOLOv8 for object detection on video with options to view and save_video results."""
    
    def __init__(self, weights):
        """Initializes the ObjectDetector class for performing inference using YOLOv8 models."""
        self.model = YOLO(weights)

    def object_detection(self, image: cv2.typing.MatLike) -> List[dict]:
        """
        np frame -> List[dict]로 return하게만 만들기

        results: [{'x': 20, 'y': 30, 'width': 100, 'height': 200, 'class_name': 'car', 'confidence': 0.9}]
        """
        # YOLOv8 Inference - image의 shape과 type은 다음과 같음
        # shape: (360, 640, 3) -> NWHC, type: <class 'numpy.ndarray'> -> numpy.ndarray
        results = self.model(image)
        prediction = []
        # process results of inference
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])  # Bounding box coordinates
            class_id = int(result.cls[0])  # Class ID
            class_name = str(self.model.names[class_id]) # Class name
            confidence = result.conf[0]  # Confidence score
            prediction.append({'x': x1, 'y': y1, 'width': x2-x1, 'height': y2-y1, 'class_name': class_name, 'confidence': confidence})
        

        return prediction

