from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, storage
from dotenv import load_dotenv

load_dotenv()

# ---------------- INIT FLASK ----------------
app = Flask(__name__)

# ---------------- INIT FIREBASE ----------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('databaseurl'),
    # 'storageBucket': os.getenv('storagebucket')
})

# ---------------- LOAD ENCODINGS ----------------
print("Loading encode file...")
with open("EncodeFileFaceRecognition.p", "rb") as file:
    encodelistknown, studentids = pickle.load(file)
print("Encodings loaded.")

# ---------------- RESOURCES ----------------
imgBackground = cv2.imread("resources/background.png")
foldermodepath = "resources/folders"
modepathlist = os.listdir(foldermodepath)
imgmodellist = [cv2.imread(os.path.join(foldermodepath, path)) for path in modepathlist]

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

modeType = 0
counter = 0
id = -1
studentinfo = None


def generate_frames():
    global modeType, counter, id, studentinfo

    while True:
        success, img = cap.read()
        if not success:
            break

        imgsmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgsmall = cv2.cvtColor(imgsmall, cv2.COLOR_BGR2RGB)

        facecurrentFrame = face_recognition.face_locations(imgsmall)
        enccodecurrFrame = face_recognition.face_encodings(imgsmall, facecurrentFrame)

        imgBg = imgBackground.copy()
        imgBg[178:178 + 480, 61:61 + 640] = img
        imgBg[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]

        if facecurrentFrame:
            for encodeface, faceloc in zip(enccodecurrFrame, facecurrentFrame):
                matches = face_recognition.compare_faces(encodelistknown, encodeface)
                facedistance = face_recognition.face_distance(encodelistknown, encodeface)
                matchindex = np.argmin(facedistance)

                if matches[matchindex]:
                    y1, x2, y2, x1 = faceloc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
                    imgBg = cvzone.cornerRect(imgBg, bbox, rt=0)
                    id = studentids[matchindex]

                    if counter == 0:
                        cvzone.putTextRect(imgBg, "Loading...", (905, 460), thickness=2)
                        counter = 1
                        modeType = 1

        if counter != 0:
            if counter == 1:
                studentinfo = db.reference(f'Students/{id}').get()

                datetimeobject = datetime.strptime(studentinfo['last_attendance'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeobject).total_seconds()

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}/')
                    studentinfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentinfo['total_attendance'])
                    ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBg[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]

                if counter <= 10 and studentinfo:
                    cv2.putText(imgBg, str(studentinfo['total_attendance']), (863, 129),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                    cv2.putText(imgBg, str(studentinfo['branch']), (1018, 578),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    (w, h), _ = cv2.getTextSize(studentinfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (444 - w) // 2

                    cv2.putText(imgBg, str(studentinfo['name']), (820 + offset, 464),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    cv2.putText(imgBg, str(studentinfo['id']), (1018, 518),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBg, str(studentinfo['year']), (913, 658),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBg, str(studentinfo['graduate_year']), (1028, 658),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBg, str(studentinfo['standing_year']), (1134, 658),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentinfo = None

        ret, buffer = cv2.imencode('.jpg', imgBg)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No file selected", 400

    filename = os.path.join("images", file.filename)
    file.save(filename)

    # Upload to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f"images/{file.filename}")
    blob.upload_from_filename(filename)

    # 🔄 Update encodings
    update_encodings()

    return redirect(url_for('upload_data_page'))



# ---------------- UPLOAD DATA FORM ----------------
@app.route('/upload_data')
def upload_data_page():
    return render_template('upload_data.html')


@app.route('/add_firebase', methods=['POST'])
def add_firebase():
    student_id = request.form['student_id']
    data = {
        "name": request.form['name'],
        "branch": request.form['branch'],
        "year": request.form['year'],
        "graduate_year": request.form['graduate_year'],
        "total_attendance": int(request.form['total_attendance']),
        "last_attendance": request.form['last_attendance'],
        "id": request.form['student_unique_id'],
        "standing_year": request.form['standing_year']
    }

    ref = db.reference("Students")
    ref.child(student_id).set(data)

    return "Data Uploaded Successfully!"

def update_encodings():
    import cv2, face_recognition, pickle, os

    folderpath = "images"
    pathlist = os.listdir(folderpath)
    imglist = []
    studentids = []
    for path in pathlist:
        imglist.append(cv2.imread(os.path.join(folderpath, path)))
        studentids.append(os.path.splitext(path)[0])

    encodelist = []
    for img in imglist:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)

    encodelistknownIds = [encodelist, studentids]
    with open("EncodeFileFaceRecognition.p", 'wb') as file:
        pickle.dump(encodelistknownIds, file)

    print("✅ Encodings updated successfully.")


if __name__ == "__main__":
    app.run(debug=True)
