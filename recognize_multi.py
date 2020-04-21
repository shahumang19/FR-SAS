from FaceDetectionSSD import FaceDetectionSSD
from Facenet import Facenet
from ThreadedStreaming import WebcamVideoStream, FileVideoStream
from threading import Thread
from datetime import datetime
import utils as u
import cv2, numpy as np
import os
import imutils
import keyboard

SOURCE_CAM = 0
DEFAULT_THRESH = 0.75
SKIP_FRAMES = 15
DATA_DIR = "data"
DISTANCE_FILE = os.path.join(DATA_DIR, "distance.euc")
LABELS_FILE = os.path.join(DATA_DIR, "embeddings.pkl")
CAM_FILE = os.path.join(DATA_DIR, "vidconfig.txt")
CONFIG_FILE = os.path.join(DATA_DIR, "config.txt")
DB_TIMESTAMP = 10



#Initializing exit Thread
def exit_check(cams):
    global infinite # Loop variable
    input()
    for cam in cams:
        cam.stop()
    infinite = False
    print("[INFO] [recognize_multi.py] Processing stopped by user...")
    # exit(0)


u.file_check(DISTANCE_FILE, "recognize_multi.py", "No User exists. Add a user...")
u.file_check(LABELS_FILE, "recognize_multi.py", "User names not found...")
u.file_check(CAM_FILE, "recognize_multi.py", "Cam file not found...")
u.file_check(CONFIG_FILE, "recognize_multi.py", "Config file not found...")


annoy_object = u.load_index(DISTANCE_FILE)
print("[INFO] [recognize_multi.py] Distance file loaded...")

labels = u.read_data(LABELS_FILE)["labels"]
print("[INFO] [recognize_multi.py] Labels file loaded...")

cam_links = u.read_txtfile(CAM_FILE)
print("[INFO] [recognize_multi.py] cam file loaded...")

configs = eval(u.read_txtfile(CONFIG_FILE)[0])
TIMESTAMP = configs["time_stamp"]
print("[INFO] [recognize_multi.py] cam file loaded...")

detector = FaceDetectionSSD()
facenet = Facenet()


# cams = [FileVideoStream(path=link, skip_frames=SKIP_FRAMES).start() for link in cam_links]
cams = [
    WebcamVideoStream(src=eval(link), skip_frames=SKIP_FRAMES, time_stamp=TIMESTAMP).start() for link in cam_links
    ]
# logs = {ix:[] for ix in range(len(cams))}
logs = {}

if len(cams) > 0:
    print(f"[INFO] [recognize_multi.py] Num of Cameras detected : {len(cams)}")
else:
    print(f"[ERROR] [recognize_multi.py] No cameras found...")
    exit(1)

if "time_stamp" in configs.keys():
    time_stamp = configs["time_stamp"]
    print(f"[INFO] [recognize_multi.py] Taking time stamp as {time_stamp} minutes...")
else:
    time_stamp = 10
    print("[INFO] [recognize_multi.py] Taking Default time stamp as 10 minutes...")

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("temp\\3.mp4")
# frames_list = []#########################

Thread(target=exit_check, args=(cams,), name='key_capture_thread', daemon=True).start()


try:
    infinite = True
    while infinite:
        camlinks_closed_count = 0
        # print(infinite)
        for ix, cam in enumerate(cams):
            # print(ix)
            
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
                            stuID = pred[0]
                            dist = pred[1]
                            if stuID != "Unknown":
                                log = f"{frame_time} -- {stuID} - {dist}"
                                print(log)
                                # day = frame_time.date().strftime("%d/%m/%Y")
                                # tm = frame_time.time().strftime("%H:%M:%S")
                                if stuID not in logs.keys():
                                    logs[stuID] = [{"dt":frame_time, "dist":dist}]
                                else:
                                    lastLog = logs[stuID][-1]
                                    minutes = int((frame_time - lastLog["dt"]).total_seconds()//60)
                                    print(minutes, (frame_time - lastLog["dt"]).total_seconds()//60)
                                    if minutes >= TIMESTAMP : 
                                        logs[stuID].append({"dt":frame_time, "dist":dist})
                    
                        frame = u.draw_predictions(frame, face_locations, predictions)

                # frame = imutils.resize(frame, width=min(480, frame.shape[1]))
                # frames_list.append(frame) #########################
                cv2.imshow(f"{ix}", frame)

                if cv2.waitKey(1) == 13 or camlinks_closed_count == len(cams):
                    print("[INFO] [recognize_multi.py] Processing stopped by user...")
                    for cam in cams:
                        cam.stop()
                    infinite = False


            else:
                pass
                # print(f"[INFO] [recognize_multi.py] Video frame not available : cam-index {ix} -- {cam_links[ix]}")
                # cam.stop()
                # camlinks_closed_count += 1
                # if camlinks_closed_count == len(cams):
                #     for cam in cams:
                #         cam.stop()
                #     infinite = False
                # u.writeVideo("data\\3.mp4", frames_list, 4)##################################
            
        
    
except Exception as e:
    print(f"[ERROR] [recognize_multi.py] : {e}")
finally:
    cv2.destroyAllWindows()

# Printing Logs of different cameras
for key in logs.keys():
    print(key,logs[key])
