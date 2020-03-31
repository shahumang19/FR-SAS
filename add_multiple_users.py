from FaceDetectionSSD import FaceDetectionSSD
from augmentation import augmentImage
import utils as u
import os, shutil
import cv2, numpy as np

BASE_DIR = "data"
OUTPUT_DIR = "faces"
BACKUP_DIR = "backup"

users = os.listdir(BASE_DIR)

try:
    detector = FaceDetectionSSD()

    for user in users:
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
                shutil.move(source, backup)
            else:
                print(f"[WARNING] [add_multiple_users.py] {user} has no images...")
except Exception as e:
    print(f"[ERROR] Exception ocurred [add_multiple_users.py] : {e}")