import datetime 
import cv2, numpy as np
from os import listdir
from os.path import isfile, isdir, join
from annoy import AnnoyIndex
from time import time


def write_data(data,name):
    """
    Writes data to pickle file.
    name : name of the pickle file
    """
    try:
        head = "Time \t\t\t -\t Probability \n"
        with open(name, "w") as fi:
            fi.write(head)
            fi.writelines(data)
        print(f"[INFO] File Written : {name}")
    except Exception as e:
        print(f"[ERROR] write_data : {e}")

        
def read_data(name):
    """
    Reads data from pickle file
    name : name of the pickle file
    """
    try:
        with open(name, "r") as fi:
            data = fi.readline()
            return data
    except Exception as e:
        print(f"[ERROR] read_data :  {e}")


def get_data(dir_path):
    """
    Accepts root path to the data folder and returns images and labels
    """
    x,y = [],[]
    
    try:
        dirs = [f for f in listdir(dir_path) if isdir(join(dir_path, f))]
        
        for d in dirs:
            current_dir = join(dir_path, d)
            files = [f for f in listdir(current_dir) if isfile(join(current_dir, f))]
            x += [cv2.imread(join(current_dir, f)) for f in files]#
            y += [d]*len(files)
    except Exception as e:
        print(f"[ERROR] get_data : {e}")
        
    return x, y
    

def load_images(dir_path):
    """
    Accepts root path to the images folder and returns images
    """
    images = []
    
    try:
        files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        images = [cv2.imread(join(dir_path, f)) for f in files]
    except Exception as e:
        print(f"[ERROR] load_images : {e}")
    
    return images

def draw_predictions(img,cords, predictions):
    """
    Draws predictions on images
    img : The image on which the predictions will be drawn
    cords : face locations
    predictions : The prediction list containing name and distance of each face location
    """
    img_cp = img.copy()
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.5
    
    for key in predictions.keys():
        (x,y,w,h) = cords[key]
        text = f"{predictions[key]:.4f}"
        cv2.rectangle(img_cp, (x,y), (x+w, y+h), (0,0,255), int(0.01*img_cp.shape[0]))
        (tw, th) = cv2.getTextSize(text, font, font_scale, thickness=5)[0]
        cv2.rectangle(img_cp, (x,y-th), (x+tw, y), (0,0,0), -1)
        cv2.putText(img_cp, text, (x, y), font, font_scale, (255,255,255), 4)

    return img_cp


def reduce_glare(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    out = clahe.apply(gray)
    image = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
    return image


def getNumberOfCameras():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr


def getDistance(n1, n2):
    return np.linalg.norm(n1-n2)


# def getPrediction(source, face_embeddings, threshold = 0.6):
#     predictions = {}
#     for ix, embedding in enumerate(face_embeddings):
#         dist = getDistance(source, embedding)
#         if dist <= threshold:
#             predictions[ix] = dist
#     return predictions

def getPrediction(sources, face_embeddings, threshold = 0.6):
    distances = {}
    predictions = {}

    for ix, embedding in enumerate(face_embeddings):
        distances[ix] = []
        for source in sources:
            dist = getDistance(source, embedding)
            distances[ix].append(dist)
    
    min_dist = [min(distances[key]) for key in distances.keys()]
    ind, val = np.argmin(min_dist), np.min(min_dist)

    count = 0
    for dist in distances[ind]:
        if dist <= threshold:
            count += 1

    probability = count / len(sources)
    
    if probability > 0.0:
        predictions[0] = probability

    return predictions


def convertMilSeconds(n): 
    return str(datetime.timedelta(milliseconds = n))


def writeVideo(name,frames, FPS):
    h,w = frames[0].shape[0:2]
    fourcc = cv2.VideoWriter_fourcc(*'DIVX') 
    video=cv2.VideoWriter(name, fourcc, FPS,(w,h))

    for frame in frames:
        video.write(frame)

    video.release()
    print(f"[INFO] {name} Generated...")
