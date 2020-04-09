from FaceDetectionSSD import FaceDetectionSSD
from Facenet import Facenet
import utils as u
import cv2, numpy as np
import os
import imutils

SOURCE_CAM = 0
DEFAULT_THRESH = 0.75
DATA_DIR = "data"
DISTANCE_FILE = os.path.join(DATA_DIR, "distance.euc")
LABELS_FILE = os.path.join(DATA_DIR, "embeddings.pkl")

if not os.path.exists(DISTANCE_FILE):
    print("[ERROR] [recognize.py] No User exists. Add a user...")
    exit(1)

if not os.path.exists(LABELS_FILE):
    print("[ERROR] [recognize.py] User names not found...")
    exit(1)


annoy_object = u.load_index(DISTANCE_FILE)
print("[INFO] [recognize.py] Distance file loaded...")

labels = u.read_data(LABELS_FILE)["labels"]
print("[INFO] [recognize.py] Labels file loaded...")


detector = FaceDetectionSSD()
facenet = Facenet()


count_frames, skip_frames = 0, 15
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap = cv2.VideoCapture("temp\\3.mp4")
frames_list = []#########################

try:
    while True:
        ret, frame = cap.read()

        if ret:
            face_locations = detector.detect_faces(frame)

            if len(face_locations) > 0:
                detected_faces = detector.extract_faces(frame, face_locations)
                embeddings = facenet.get_embeddings(detected_faces)
                if embeddings is None:
                    continue

                predictions = u.get_predictions(embeddings, annoy_object, labels, DEFAULT_THRESH)
                
                for pred in predictions:
                    if pred[0] != "Unknown":
                        print(f"{pred[0]} - {pred[1]}")

                frame = u.draw_predictions(frame, face_locations, predictions)

            frame = imutils.resize(frame, width=min(1024, frame.shape[1]))
            frames_list.append(frame) #########################
            # cv2.imshow("Live Face Detection", frame)
            count_frames += skip_frames # i.e. at 30 fps, this advances one second
            cap.set(1, count_frames)
            if cv2.waitKey(1) == 13:
                break
        else:
            print("[INFO] [recognize.py] Video frame not available...")
            u.writeVideo("data\\3.mp4", frames_list, 4)
            break
except Exception as e:
    print(f"[ERROR] [recognize.py] : {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
