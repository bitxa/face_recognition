import threading
import cv2
from deepface import DeepFace
from deepface.commons import functions
import os
import cv2


class LiveRecognitionThread(threading.Thread):
    def __init__(self, frame, folder_path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.frame = frame
        self.folder_path = folder_path

    def run(self):
        # Detect faces in the frame
        detected_faces = functions.extract_faces(
            self.frame, detector_backend="retinaface", enforce_detection=False)
        print(f"DETECTED FACES {detected_faces}")

        for face_info in detected_faces:

            face_coordinates = face_info[1]

            x, y, w, h = face_coordinates['x'], face_coordinates['y'], face_coordinates['w'], face_coordinates['h']
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Now we crop and analyze the face in a try-except block
            try:
                # Crop the detected face
                face_img = self.frame[y:y+h, x:x+w]

                # Recognize the cropped face
                identified_faces = DeepFace.find(
                    face_img, db_path=self.folder_path, enforce_detection=False, model_name="ArcFace", detector_backend="retinaface")
                print(f"IDENTIFIED FACES {identified_faces}")

                # If we have identified faces, we take the first match (highest probability)
                if len(identified_faces) > 0:
                    # Take the first match
                    identity = identified_faces[0]['identity'][0]
                    name = os.path.basename(
                        os.path.dirname(identity))  # Extract the name
                    cv2.putText(self.frame, name, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

            except Exception as e:
                print(f"Recognition error: {e}")

    def stop(self):
        self._stop_event.set()
