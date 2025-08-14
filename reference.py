import cv2
from pathlib import Path
import sqlite3
from datetime import datetime

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

def is_triangle(points):
    if points[0] and points[1] and points[2]:
        if (points[1][0] < points[0][0]) and (points[0][0]<points[2][0]): 
            if points[0][1] < min(points[1][1],points[2][1]): 
                return True
    return False

def extract_reference(frame):
    global ratio
    global net
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

    if is_triangle(points):
        x = abs(points[1][0] - points[2][0]) 
        h = abs(points[0][1] - (points[1][1] + points[2][1]) // 2) 
        ratio = round(x/h, 1)
        cv2.line(frame, points[0], points[1], (255, 255, 255), 2)
        cv2.line(frame, points[0], points[2], (255, 255, 255), 2)
    return

def on_mouse(event,x,y,flags,param):
    global reference
    if event == cv2.EVENT_LBUTTONDOWN:
        reference = param[0]
        save_db()

def start_reference():
    global ratio
    global reference

    cv2.namedWindow('Reference', 1)
    cv2.setMouseCallback('Reference', on_mouse, param=[ratio])
    capture = cv2.VideoCapture(0) # create streaming object

    while cv2.waitKey(1) < 0:
        # capture frame
        if reference == 0 :
            hasFrame, frame = capture.read()
            if not hasFrame:
                cv2.waitKey()
                break

            # show it on window
            cv2.imshow('Reference',frame)
            extract_reference(frame)

            # print direction message on window
            cv2.putText(frame,"Adjust your posture properly until the lines appear",
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.putText(frame,"then please click on the screen.", 
                        (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, lineType=cv2.LINE_AA)
        # pause after click
        else :
            cv2.putText(frame,"Today's posture!",
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.putText(frame,"If you want to try again, press any key to exit and restart", 
                        (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.imshow('Reference',frame)
            cv2.waitKey()
            break
    # finish video
    capture.release()
    cv2.destroyAllWindows()
    
def save_db():
    global reference
    conn = sqlite3.connect('_put your own path_')
    curs = conn.cursor()
    sql = """ DELETE FROM references WHERE date = ? """
    curs.execute(sql, (datetime.now().strftime("%Y/%m/%d"),))
    sql = """ INSERT INTO references (date, ratio) values (?, ?) """
    curs.execute(sql, (datetime.now().strftime("%Y/%m/%d"), reference))
    conn.commit()
    conn.close()
    


if __name__ == '__main__':
    load_model()
    start_reference()