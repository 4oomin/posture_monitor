import cv2
from pathlib import Path
import sqlite3
from datetime import datetime
import random
import numpy as np

nextTime=0
ratio=0
reference = None
net = None
# load model 
def load_model():
    global net
    BODY_PARTS = {"Neck": 1, "RShoulder": 2, "LShoulder": 5} # detection point
    BASE_DIR = Path(__file__).resolve().parent 
    protoFile = str(BASE_DIR) + "_put your own path_" # model network
    weightsFile = str(BASE_DIR) + "_put your own path_" # model weight
    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
    return net

def is_triangle(points):
    if points[0] and points[1] and points[2]:
        if (points[1][0] < points[0][0]) and (points[0][0]<points[2][0]): 
            if points[0][1] < min(points[1][1],points[2][1]): 
                return True
    return False

def is_time():
    global nextTime
    curr_hour = datetime.now().hour
    curr_min = datetime.now().minute
    currTime = curr_hour*60+curr_min
    if nextTime <= currTime:
        nextTime = currTime + 20 # every 20 minutes try to capture
        return True
    return False

def random_start():
    global nextTime
    curr_hour = datetime.now().hour
    curr_min = datetime.now().minute
    new_min = random.randint(curr_min+1, 60)
    nextTime =  curr_hour*60+new_min

def extract_record(frame):
    global net
    global ratio
    points = []
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    modelWidth = 320
    modelHeight = 240
    modelScale = 1.0 / 255
    
    inpBlob = cv2.dnn.blobFromImage(frame, modelScale, (modelWidth, modelHeight),
                                    (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()

    mat = [1, 2, 5] #detection point
    for j in range(3):
        i = mat[j]
        probMap = output[0, i, :, :]
        _, prob, _, point = cv2.minMaxLoc(probMap)
        x = (frameWidth * point[0]) / output.shape[3]
        y = (frameHeight * point[1]) / output.shape[2]

        if prob > 0.1:
            points.append((int(x), int(y)))
        else:
            points.append(None)
    pass

    if is_triangle(points):
        x = abs(points[1][0] - points[2][0]) 
        h = abs(points[0][1] - (points[1][1] + points[2][1]) // 2) 
        ratio = round(x/h, 1) 
        if is_time():
            save_db((datetime.now().strftime("%Y/%m/%d"),datetime.now().time().strftime("%H:%M"),ratio))
    return

def grade_posture():
    global ratio
    global reference
    w1 = 0.8 # sqrt(3)/2 30 degree
    w2 = 0.5 # 1/2 60 degree
    
    if round(reference/w1,1) <= ratio < round(reference/w2,1):
        message = "Bending 30 degrees. Adjust your posture."  
    elif round(reference/w2,1) <= ratio:
        message = "Bending 60 degrees. Adjust your posture."
    else:
        message = "Please click here and press any key to exit."
    
    img = np.zeros((100, 1000, 3), dtype=np.uint8) 
    cv2.putText(img,message,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.imshow("Monitor", img)


def start_monitor():

    if reference is None:
        return # capture reference first
    
    cv2.namedWindow('Monitor', 1) # waring message window
    capture = cv2.VideoCapture(0) # create streaming object
    while cv2.waitKey(1) < 0:
        # capture frame
        hasFrame, frame = capture.read()
        if not hasFrame:
            cv2.waitKey()
            break
   
        extract_record(frame)
        grade_posture()

    # finish video
    capture.release()
    cv2.destroyAllWindows()

def load_refer():
    global reference 
    conn = sqlite3.connect('_put your own path_')
    curs = conn.cursor()
    sql = """ SELECT ratio FROM references WHERE date = ?"""
    curs.execute(sql, (datetime.now().strftime("%Y/%m/%d"),))
    reference= curs.fetchone()
    if reference is not None:
        reference= reference[0]
    conn.close()

def save_db(record):
    conn = sqlite3.connect('_put your own path_')
    curs = conn.cursor()
    sql = """ INSERT INTO monitors (date, time, ratio) values (?, ?, ?) """
    curs.execute(sql, (record[0],record[1],record[2]))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    load_model()
    load_refer()
    random_start()
    start_monitor()