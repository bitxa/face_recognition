# video_capture_module.py

import cv2
import os

def capture_frames(name, capture_duration=5, video_source=0):
    person_dir = os.path.join("captured_faces", name)
    os.makedirs(person_dir, exist_ok=True)

    video_capture = cv2.VideoCapture(video_source)
    
    if not video_capture.isOpened():
        raise IOError("Cannot open webcam")

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(capture_duration * fps)

    try:
        for i in range(frame_count):
            ret, frame = video_capture.read()
            
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            frame_filename = os.path.join(person_dir, f"{name}_{i}.jpg")
            cv2.imwrite(frame_filename, frame)
            cv2.imshow('Capturing Faces', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video_capture.release()
        cv2.destroyAllWindows()
