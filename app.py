from flask import Flask, render_template, Response
from datetime import datetime
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, db

# --- INITIALIZATION ---
app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-93ab5-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-93ab5.appspot.com"
})

# Load Resources
imgBackground = cv2.imread("resources/background.png")
folder_mode_path = "resources/folders"
mode_path_list = os.listdir(folder_mode_path)
imgmodellist = [cv2.imread(os.path.join(folder_mode_path, path)) for path in mode_path_list]

print("Loading Encode File...")
with open("EncodefileFaceRecognition.p", 'rb') as file:
    encode_list_known_with_ids = pickle.load(file)
encodelistknown, studentids = encode_list_known_with_ids
print("Encode File Loaded")

# Global variables to manage state
modeType = 0
counter = 0
student_id = -1
studentInfo = {}

# --- VIDEO STREAMING GENERATOR ---
def generate_frames():
    """
    This function captures frames from the camera, performs face recognition,
    and yields them as a byte stream for the M-JPEG response.
    """
    global modeType, counter, student_id, studentInfo
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            # Face Recognition Logic
            imgsmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgsmall = cv2.cvtColor(imgsmall, cv2.COLOR_BGR2RGB)

            facecurrentFrame = face_recognition.face_locations(imgsmall)
            enccodecurrFrame = face_recognition.face_encodings(imgsmall, facecurrentFrame)
            
            # Create a copy of the background to draw on
            current_background = imgBackground.copy()
            current_background[178:178 + 480, 61:61 + 640] = img
            current_background[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]
            
            if facecurrentFrame:
                for encodeface, faceloc in zip(enccodecurrFrame, facecurrentFrame):
                    matches = face_recognition.compare_faces(encodelistknown, encodeface)
                    facedistance = face_recognition.face_distance(encodelistknown, encodeface)
                    matchindex = np.argmin(facedistance)

                    if matches[matchindex]:
                        y1, x2, y2, x1 = faceloc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = (61 + x1, 178 + y1, x2 - x1, y2 - y1)
                        cvzone.cornerRect(current_background, bbox, rt=0)
                        student_id = studentids[matchindex]

                        if counter == 0:
                            counter = 1
                            modeType = 1
            
            if counter != 0:
                if counter == 1:
                    studentInfo = db.reference(f'Students/{student_id}').get()
                    if studentInfo:
                        datetimeobject = datetime.strptime(studentInfo['last_attendance'], "%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeobject).total_seconds()
                        
                        if secondsElapsed > 30:
                            ref = db.reference(f'Students/{student_id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            modeType = 3
                            counter = 0
                            current_background[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]
                
                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2
                    
                    current_background[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]

                    if counter <= 10:
                        cv2.putText(current_background, str(studentInfo['total_attendance']), (863, 129), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (444 - w) // 2
                        cv2.putText(current_background, str(studentInfo['name']), (820 + offset, 464), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    
                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = {}
                        student_id = -1
                        current_background[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]
            else:
                modeType = 0
                counter = 0

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', current_background)
            frame = buffer.tobytes()
            # Yield the frame in the format required for M-JPEG stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# --- FLASK ROUTES ---
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)