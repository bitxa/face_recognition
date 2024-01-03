# trainer.py

import cv2
import os
import tempfile

def capture_frames(capture_duration=5):
    temp_dir = tempfile.mkdtemp()
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        raise IOError("Cannot open webcam")

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(capture_duration * fps)
    saved_frames = []

    try:
        for i in range(frame_count):
            ret, frame = video_capture.read()
            if not ret:
                break
            
            frame_filename = os.path.join(temp_dir, f"frame_{i}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frames.append(frame_filename)
            
            cv2.imshow('Video Capture', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video_capture.release()
        cv2.destroyAllWindows()

    return temp_dir, saved_frames
