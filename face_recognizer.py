from typing import List, Tuple
from dataclasses import dataclass

import mediapipe as mp

faceDetection = mp.solutions.face_detection.FaceDetection()
mpdraw = mp.solutions.drawing_utils

@dataclass
class Detection:
    entity: str
    confidence_score: float
    bounding_box: Tuple[float, float, float, float]

class FaceRecognizer():
    def __init__(self, entities=["person"], confidence_score=0.7):
        self.entities = entities
        self.confidence_score = confidence_score

    def recognize(self, frame) -> List[Detection]:
        detection = faceDetection.process(frame)
        results = []
        if not detection.detections:
            return results

        for result in detection.detections:
            box = result.location_data.relative_bounding_box
            h, w, _ = frame.shape

            box_scaled = int(w*box.xmin), int(h*box.ymin), int(w*box.width), int(h*box.height)
            score = result.score[0]
            if (score > self.confidence_score):
                results.append(Detection("PERSON", confidence_score=score, bounding_box=box_scaled))
        return results
