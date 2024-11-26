from typing import List

import cv2


def object_detection(image: cv2.typing.MatLike) -> List[dict]:
    """
    np frame -> List[dict]로 return하게만 만들기
    results: [{'x': 20, 'y': 30, 'width': 100, 'height': 200, 'class_name': 'car'}]
    """
    pass
