import numpy as np
import cv2 as cv
import os
from scipy import spatial
import pickle
def predictorr(src,mod,dec,pkldbb):

    def resz3(h, w, img):

        hz = np.zeros((h, w, 3))
        for i in range(3):
            hz[:, :, i] = cv.resize(img[:, :, i], (w, h))

        return hz


    imgarray = cv.imread(src)
    pkldata = pkldbb
    pklpath = os.path.join(pkldata)

    faces = dec.detect_faces(imgarray)
    print(f"Detected {len(faces)} Faces")
    fontScale = 3
    fontColor = (10, 5, 10)
    lineType = 2
    font = cv.FONT_HERSHEY_SIMPLEX
    thickness1 = 4
    present = []
    # newimg=cv.resize(imgarray,(160,160))
    for i in faces:
        x, y, w, h = i['box']
        keyp = i['keypoints']
        con = i['confidence']
        con = np.round(con, 2)
        if con > 0.8:

            x = abs(x)
            y = abs(y)
            nimg = imgarray[y:y + h, x:x + w, :]
            nimg = resz3(224, 224, nimg)
            f1 = mod.predict(nimg.reshape(-1, 224, 224, 3, 1))
            mainsim = []
            tpkls = [i for i in os.listdir(pkldata)]
            for pkls in os.listdir(pklpath):
                similaritiesin = []
                file = open(f'{pklpath}/{pkls}', 'rb')
                data = pickle.load(file)
                file.close()
                for f in data:
                    dis = spatial.distance.cosine(f1, f)
                    similaritiesin.append(dis)

                mainsim.append(min(similaritiesin))
            stud = tpkls[np.argmin(mainsim)]
            pos1 = np.random.randint(255)
            pos2 = np.random.randint(255)
            pos3 = np.random.randint(255)
            start_point = (x, y)
            color = (pos1, pos2, pos3)
            # Ending coordinate, here (220, 220)
            # represents the bottom right corner of rectangle
            end_point = (x + w, y + h)
            bottomLeftCornerOfText = (x, y - 6)

            # Using cv2.rectangle() method
            # Draw a rectangle with blue line borders of thickness of 2 px
            imgarray = cv.rectangle(imgarray, start_point, end_point, color, thickness1)
            imgarray = cv.putText(imgarray, str(con),
                                  (x, y - 55),
                                  font,
                                  1,
                                  color,
                                  lineType)
            imgarray = cv.putText(imgarray, stud,
                                  bottomLeftCornerOfText,
                                  font,
                                  fontScale,
                                  color,
                                  lineType)
            present.append(stud)
    return {'image':imgarray,'present':present}


