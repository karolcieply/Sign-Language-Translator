# translate List[base64] to List[ndarray] using opencv

import cv2
import numpy as np
import base64


def base64_to_ndarray(base64_images: list[str]) -> list[np.ndarray]:
    return [cv2.cvtColor(cv2.imdecode(np.frombuffer(base64.b64decode(image), np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_RGB2BGR) for image in base64_images]

