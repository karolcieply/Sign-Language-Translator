"""Module for """
import base64
import cv2
import h5py
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model


class TranslationService:
    """Serivce for translating sign language to text."""

    def __init__(self):
        """"""
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.model = load_model("backend/model.h5")
        self.classes = ["good_job","hello","sleep","thank_you","victory"]

    def holistic_detection(self, image, model):
        """
        Przetwarza obraz za pomocą modelu MediaPipe Holistic.
    
        Args:
            image (np.array): Obraz wejściowy w formacie BGR.
            model (mp.solutions.holistic.Holistic): Model MediaPipe Holistic.
    
        Returns:
            tuple:
                - np.array: Przetworzony obraz w formacie BGR.
                - object: Wyniki przetwarzania zawierające landmarki i inne dane.
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = model.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, results

    def get_points(self, raw_points):
        """
        Ekstrahuje współrzędne landmarków z wyników MediaPipe i zwraca je jako spłaszczoną tablicę NumPy.

        Args:
            raw_points (object): Wyniki przetwarzania MediaPipe zawierające landmarki.

        Returns:
            np.array: Spłaszczona tablica współrzędnych landmarków.
                - Pose landmarks: (33 * 4) współrzędne (x, y, z, visibility).
                - Face landmarks: (468 * 3) współrzędne (x, y, z).
                - Left hand landmarks: (21 * 3) współrzędne (x, y, z).
                - Right hand landmarks: (21 * 3) współrzędne (x, y, z).
                Jeśli brak odpowiednich landmarków, zwracane są tablice wypełnione zerami.
        """
        pose = np.array([[res.x, res.y, res.z, res.visibility] for res in raw_points.pose_landmarks.landmark]).flatten() if raw_points.pose_landmarks else np.zeros(33 * 4)
        face = np.array([[res.x, res.y, res.z] for res in raw_points.face_landmarks.landmark]).flatten() if raw_points.face_landmarks else np.zeros(468 * 3)
        lh = np.array([[res.x, res.y, res.z] for res in raw_points.left_hand_landmarks.landmark]).flatten() if raw_points.left_hand_landmarks else np.zeros(21 * 3)
        rh = np.array([[res.x, res.y, res.z] for res in raw_points.right_hand_landmarks.landmark]).flatten() if raw_points.right_hand_landmarks else np.zeros(21 * 3)
        return np.concatenate([pose, face, lh, rh])

    def process_frames(self, frames: list[str]) -> str:
        to_model = []
        holistic_model = self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        for element in frames:
            image_b64 = element.split(",")[1]
            binary = base64.b64decode(image_b64)
            np_image = np.frombuffer(binary, dtype=np.uint8)
            image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
            image, mp_detection = self.holistic_detection(image, holistic_model)
            to_model.append(self.get_points(mp_detection))

        res = self.model.predict(np.expand_dims(to_model, axis=0))
        return self.classes[np.argmax(res)]


translation_service = TranslationService()
