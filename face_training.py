import face_recognition
import os

def train_faces_from_directory(directory):
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            image_path = os.path.join(directory, filename)
            frame_image = face_recognition.load_image_file(image_path)
            frame_face_encodings = face_recognition.face_encodings(frame_image)

            if frame_face_encodings:
                known_face_encodings.append(frame_face_encodings[0])
                known_face_names.append("Person")

    return known_face_encodings, known_face_names
