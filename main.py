import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone

cap=cv2.VideoCapture(0)
cap.set(3,640)  # Set width
cap.set(4,480)  # Set height

imgBackground = cv2.imread("resources/background.png")

# importing mode list
foldermodepath = "resources/folders"
modepathlist = os.listdir(foldermodepath)
imgmodellist = []
for path in modepathlist:
    imgmodellist.append(cv2.imread(os.path.join(foldermodepath,path)))

# print(len(imgmodellist))


#load encodings file
print("load encode file... ")
file = open("EncodefileFaceRecognition.p",'rb')
encodelistknownIds = pickle.load(file)
file.close()
encodelistknown,studentids = encodelistknownIds
#print(studentids)
print("Encoded file loaded")

while True:
    success, img=cap.read()

    imgsmall = cv2.resize(img,(0,0),None, 0.25, 0.25) #resize the image
    imgsmall = cv2.cvtColor(imgsmall,cv2.COLOR_BGR2RGB)

    facecurrentFrame = face_recognition.face_locations(imgsmall)


    #encode for new life image to validate the saved and live image
    enccodecurrFrame = face_recognition.face_encodings(imgsmall,facecurrentFrame)

    imgBackground[178:178+480 , 61:61+640] = img
    imgBackground[46:46+666 , 810:810+444] = imgmodellist[1]

    for encodeface, faceloc in zip(enccodecurrFrame,facecurrentFrame):
        matches = face_recognition.compare_faces(encodelistknown,encodeface)
        facedistance = face_recognition.face_distance(encodelistknown,encodeface)
        # print("matches",matches)
        # print("matches", [bool(match) for match in matches]) #i use this because i want to remove np.true , np.false to ture and false
        # print("facedistance",facedistance)

        matchindex = np.argmin(facedistance)
        #print("matchindex", matchindex)

        if matches[matchindex]:
              # print("match found")
           y1, x2, y2, x1 = faceloc
           y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

           bbox = (55+x1, 162+y1, x2 - x1, y2 - y1)
           cvzone.cornerRect(imgBackground,bbox,rt=0)

    cv2.imshow("webcam", img)
    cv2.imshow("Face Attendence",imgBackground)
    cv2.waitKey(1)

