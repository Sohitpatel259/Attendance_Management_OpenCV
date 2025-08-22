from datetime import datetime
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-93ab5-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-93ab5.appspot.com"
})

# bucket = storage.bucket()

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


modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img=cap.read()

    imgsmall = cv2.resize(img,(0,0),None, 0.25, 0.25) #resize the image
    imgsmall = cv2.cvtColor(imgsmall,cv2.COLOR_BGR2RGB)

    facecurrentFrame = face_recognition.face_locations(imgsmall)


    #encode for new life image to validate the saved and live image
    enccodecurrFrame = face_recognition.face_encodings(imgsmall,facecurrentFrame)

    imgBackground[178:178+480 , 61:61+640] = img
    imgBackground[46:46+666 , 810:810+444] = imgmodellist[modeType]
    # imgBackground[44:44+633 , 808:808+414] = imgmodellist[0]

    
    if facecurrentFrame:

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
                imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=0)
                id = studentids[matchindex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading...", (905, 460),  thickness=2)
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter=1
                    modeType = 1 
        
        if counter!=0:

            if counter ==1:
                studentinfo = db.reference(f'Students/{id}').get()
                print(studentinfo)

                # blob = bucket.get_blob(f'Images/{id}.png')
                # array = np.frombuffer(blob.download_as_string(), np.uint8)
                # imgStudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                # what time should we choose to update another attendance record?

                datetimeobject = datetime.strptime(studentinfo['last_attendance'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeobject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}/')
                    studentinfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentinfo['total_attendance'])
                    ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    # studentinfo['attendance_history'].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    modeType = 3
                    counter = 0
                    imgBackground[46:46+666 , 810:810+444] = imgmodellist[modeType]



            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[46:46+666 , 810:810+444] = imgmodellist[modeType]

                if counter <= 10:

                    # cv2.putText(imgBackground, str(studentinfo['total_attendance']), (1020, 183), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(imgBackground, str(studentinfo['total_attendance']), (863, 129), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                    # (w,h),_ = cv2.getTextSize(studentinfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 2)
                    # offset = (200-w)//2
                    (w,h),_ = cv2.getTextSize(studentinfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (444-w)//2

                    cv2.putText(imgBackground, str(studentinfo['name']), (820+offset, 464), cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,50), 1)
                    # cv2.putText(imgBackground, str(studentinfo['branch']), (810, 670), cv2.FONT_HERSHEY_COMPLEX, 1, (75,12,130), 2)
                    cv2.putText(imgBackground, str(studentinfo['branch']), (1018, 578), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                    cv2.putText(imgBackground, str(studentinfo['id']), (1018, 518), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                    

                    # cv2.putText(imgBackground, str(studentinfo['year']), (1060, 670), cv2.FONT_HERSHEY_COMPLEX, 1, (75,12,130), 2)
                    cv2.putText(imgBackground, str(studentinfo['year']), (913, 658), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    # cv2.putText(imgBackground, str(studentinfo['last_attendance']), (810, 705), cv2.FONT_HERSHEY_COMPLEX, 1, (75,12,130), 2)
                    # cv2.putText(imgBackground, str(studentinfo['attendance_history']), (935, 680), cv2.FONT_HERSHEY_COMPLEX, 1, (75,12,130), 2)
                    # cv2.putText(imgBackground, str(studentinfo['graduate_year']), (810, 80), cv2.FONT_HERSHEY_COMPLEX, 1, (75,12,130), 2)
                    cv2.putText(imgBackground, str(studentinfo['graduate_year']), (1028,658), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    cv2.putText(imgBackground, str(studentinfo['standing_year']), (1134, 658), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)


                    # imgBackground[162:162+480, 55:55+640] = imgStudent
                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentinfo = []
                    imgStudent = []
                    imgBackground[46:46+666 , 810:810+444] = imgmodellist[modeType]

    else:
        modeType = 0
        counter = 0

    cv2.imshow("webcam", img)
    cv2.imshow("Face Attendance",imgBackground)
    cv2.waitKey(1)

