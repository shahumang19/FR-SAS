from FaceDetectionSSD import FaceDetectionSSD
from augmentation import augmentImage
from framsdb import FRAMSDatabase
import utils as u
import os, shutil
import cv2, numpy as np

BASE_DIR = "original"
OUTPUT_DIR = "faces"
BACKUP_DIR = "backup"
DATA_DIR = "data"

CONFIG_FILE = os.path.join(DATA_DIR, "config.txt")

u.file_check(CONFIG_FILE, "add_multiple_users.py", "Config file not found...")

configs = eval(u.read_txtfile(CONFIG_FILE)[0])
dbConfig = configs["db"]
host, user, passwd, dbname = dbConfig["host"], dbConfig["user"], dbConfig["passwd"], dbConfig["db"]
print("[INFO] [recognize_multi.py] DB configs file loaded...")

users = os.listdir(BASE_DIR)
db = FRAMSDatabase(host, user, passwd, dbname)

try:
    detector = FaceDetectionSSD()

    for user in users:
        sid, sclass, sname = user.split("_")
        source = os.path.join(BASE_DIR, user)
        dest = os.path.join(OUTPUT_DIR, user)
        backup = os.path.join(BACKUP_DIR, user)
        print(f"[INFO] [add_multiple_users.py] User under process : {user}")

        if os.path.exists(dest):
            print(f"[WARNING] [add_multiple_users.py] {user} already exists...")
        else:
            os.mkdir(dest)
            files = os.listdir(source)
            if len(files) > 0:
                for file in files:
                    source_file = os.path.join(source, file)
                    img = cv2.imread(source_file)

                    if img is not None:
                        face_locations = detector.detect_faces(img)
                        if len(face_locations) > 0:
                            face = detector.extract_faces(img, face_locations)[0]
                            augmentedFaces = augmentImage(face)
                            for ix, aface in enumerate(augmentedFaces, start=1):
                                cv2.imwrite(os.path.join(dest, f"{ix}_{file}"), aface)
                            del augmentedFaces, face
                        else:
                            print(f"[ERROR] [add_multiple_users.py] No faces found : {source_file}")
                        del img
                    else:
                        print(f"[ERROR] [add_multiple_users.py] {source_file} not an image...")
                inserted = db.addStudent(sid, sname, sclass, 1)
                if inserted >= 1:
                    shutil.move(source, backup)
                elif inserted == -1:
                    shutil.rmtree(dest)
                    print(f"[ERROR] [add_multiple_users.py] {sid} {sname} - User id Exists...")
                else:
                    print(f"[ERROR] [add_multiple_users.py] {sid} {sname} - not added to DB...")
            else:
                print(f"[WARNING] [add_multiple_users.py] {user} has no images...")
except Exception as e:
    print(f"[ERROR] Exception ocurred [add_multiple_users.py] : {e}")
finally:
    db.close()