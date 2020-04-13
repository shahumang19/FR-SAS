from FaceDetectionSSD import FaceDetectionSSD
from Facenet import Facenet
from ThreadedStreaming import WebcamVideoStream, FileVideoStream
import utils as u
import cv2, numpy as np
import os
import imutils

SOURCE_CAM = 0
DEFAULT_THRESH = 0.75
SKIP_FRAMES = 15
DATA_DIR = "data"
DISTANCE_FILE = os.path.join(DATA_DIR, "distance.euc")
LABELS_FILE = os.path.join(DATA_DIR, "embeddings.pkl")
CONFIG_FILE = os.path.join(DATA_DIR, "config.txt")


if not os.path.exists(DISTANCE_FILE):
    print("[ERROR] [recognize_multi.py] No User exists. Add a user...")
    exit(1)

if not os.path.exists(LABELS_FILE):
    print("[ERROR] [recognize_multi.py] User names not found...")
    exit(1)

if not os.path.exists(CONFIG_FILE):
    print("[ERROR] [recognize_multi.py] config file not found...")
    exit(1)


annoy_object = u.load_index(DISTANCE_FILE)
print("[INFO] [recognize_multi.py] Distance file loaded...")

labels = u.read_data(LABELS_FILE)["labels"]
print("[INFO] [recognize_multi.py] Labels file loaded...")

cam_links = u.read_txtfile(CONFIG_FILE)
print("[INFO] [recognize_multi.py] configs file loaded...")

detector = FaceDetectionSSD()
facenet = Facenet()


cams = [FileVideoStream(path=link, skip_frames=SKIP_FRAMES).start() for link in cam_links]
# cams = [WebcamVideoStream(src=link, skip_frames=SKIP_FRAMES).start() for link in cam_links]
logs = {ix:[] for ix in range(len(cams))}
print(f"[INFO] [recognize_multi.py] Num of Cameras detected : {len(cams)}")

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("temp\\3.mp4")
# frames_list = []#########################

try:
    infinite = True
    while infinite:
        camlinks_closed_count = 0
        print(infinite)
        for ix, cam in enumerate(cams):
            print(ix)
            
            # if cam.grabbed:
            if cam.more():
                frame_time, frame = cam.read()
                face_locations = detector.detect_faces(frame)

                if len(face_locations) > 0:
                    detected_faces = detector.extract_faces(frame, face_locations)
                    embeddings = facenet.get_embeddings(detected_faces)
                    if embeddings is not None:
                        predictions = u.get_predictions(embeddings, annoy_object, labels, DEFAULT_THRESH)
                    
                        for pred in predictions:
                            if pred[0] != "Unknown":
                                log = f"cam-{ix} -- {frame_time} -- {pred[0]} - {pred[1]}\n"
                                logs[ix].append(log)
                                print(log, end="")
                    
                        frame = u.draw_predictions(frame, face_locations, predictions)

                # frame = imutils.resize(frame, width=min(480, frame.shape[1]))
                # frames_list.append(frame) #########################
                # cv2.imshow(f"{ix}", frame)

                if cv2.waitKey(1) == 13 or camlinks_closed_count == len(cams):
                    print("[INFO] [recognize_multi.py] Processing stopped by user...")
                    for cam in cams:
                        cam.stop()
                    infinite = False
            else:
                print(f"[INFO] [recognize_multi.py] Video frame not available : cam-index {ix} -- {cam_links[ix]}")
                # cam.stop()
                camlinks_closed_count += 1
                if camlinks_closed_count == len(cams):
                    for cam in cams:
                        cam.stop()
                    infinite = False
                # u.writeVideo("data\\3.mp4", frames_list, 4)##################################
    
except Exception as e:
    print(f"[ERROR] [recognize_multi.py] : {e}")
finally:
    cv2.destroyAllWindows()

    # Printing Logs of different cameras
    for key in logs.keys():
        for log in logs[key]:
            print(log, end="")
