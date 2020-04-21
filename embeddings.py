from Facenet import Facenet
from framsdb import FRAMSDatabase
import cv2, numpy as np
import utils as u
import os, shutil

BASE_DIR = "faces"
DATA_DIR = "data"
EMBEDDINGS_FILE = os.path.join(DATA_DIR, "embeddings.pkl")
DISTANCE_FILE = os.path.join(DATA_DIR, "distance.euc")
CONFIG_FILE = os.path.join(DATA_DIR, "config.txt")

u.file_check(CONFIG_FILE, "add_multiple_users.py", "Config file not found...")

configs = eval(u.read_txtfile(CONFIG_FILE)[0])
dbConfig = configs["db"]
host, user, passwd, dbname = dbConfig["host"], dbConfig["user"], dbConfig["passwd"], dbConfig["db"]
print("[INFO] [recognize_multi.py] DB configs file loaded...")


users = os.listdir(BASE_DIR)
db = FRAMSDatabase(host, user, passwd, dbname)

try:
    facenet = Facenet()
    images, labels = [], []

    for user in users:
        sid, sclass, sname = user.split("_")
        source = os.path.join(BASE_DIR, user)
        print(f"[INFO] [embeddings.py] User under process : {user}")

        files = os.listdir(source)
        if len(files) > 0:
            
            for file in files:
                source_file = os.path.join(source, file)
                img = cv2.imread(source_file)

                if img is not None:
                    images.append(img)
                    labels.append(sid)
                else:
                    print(f"[ERROR] [embeddings.py] {source_file} not an image...")
            shutil.rmtree(source)
        else:
            print(f"[WARNING] [embeddings.py] {user} has no images...")

    if len(images) > 0:
        embeddings = facenet.get_embeddings(images, verbose=1)
        
        if embeddings is not None:
            data = None
            if os.path.exists(EMBEDDINGS_FILE):
                data = u.read_data(EMBEDDINGS_FILE)
                data["embeddings"] = np.append(data["embeddings"], embeddings, axis=0)
                data["labels"] += labels
                u.write_data(data, EMBEDDINGS_FILE)
            else:
                data = {"embeddings":embeddings, "labels":labels}
                u.write_data(data, EMBEDDINGS_FILE)
            u.generate_annoyIndex(data["embeddings"], name=DISTANCE_FILE, trees=20)
    else:
        print(f"[ERROR] [embeddings.py] No images found in {BASE_DIR}...")

except Exception as e:
    print(f"[ERROR] Exception ocurred [embeddings.py] : {e}")