from flask import Flask, render_template, Response, request, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import os
import pickle
import numpy as np

# Try to import face_recognition, gracefully handle if not available
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    # Some consoles can't encode emoji — use a safe print helper below
    
    def safe_print(msg):
        try:
            print(msg)
        except UnicodeEncodeError:
            # Fallback: remove non-ascii characters
            try:
                print(msg.encode('ascii', 'ignore').decode('ascii'))
            except Exception:
                # Last resort
                print(str(msg))

    safe_print("✅ Face recognition loaded successfully")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    # ensure helper exists in the import-failure path
    def safe_print(msg):
        try:
            print(msg)
        except UnicodeEncodeError:
            try:
                print(msg.encode('ascii', 'ignore').decode('ascii'))
            except Exception:
                print(str(msg))

    safe_print("⚠️ Face recognition not available - using basic detection only")

from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, storage
from dotenv import load_dotenv

# Simple replacements for cvzone functions
def cornerRect(img, bbox, rt=1, colorR=(255, 0, 255), colorC=(0, 255, 0), thickness=2):
    x, y, w, h = bbox
    x1, y1 = x + w, y + h
    
    # Draw corner rectangles
    cv2.rectangle(img, (x, y), (x + rt, y + rt), colorR, cv2.FILLED)
    cv2.rectangle(img, (x1 - rt, y), (x1, y + rt), colorR, cv2.FILLED)
    cv2.rectangle(img, (x, y1 - rt), (x + rt, y1), colorR, cv2.FILLED)
    cv2.rectangle(img, (x1 - rt, y1 - rt), (x1, y1), colorR, cv2.FILLED)
    
    # Draw rectangle
    cv2.rectangle(img, (x, y), (x1, y1), colorC, thickness)
    return img

def putTextRect(img, text, pos, scale=1, thickness=1, colorT=(255, 255, 255), colorR=(255, 0, 255), offset=10):
    x, y = pos
    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    cv2.rectangle(img, (x - offset, y - h - offset), (x + w + offset, y + offset), colorR, cv2.FILLED)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, colorT, thickness)
    return img

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
if FACE_RECOGNITION_AVAILABLE:
    safe_print("Loading encode file...")
    try:
        with open("EncodeFileFaceRecognition.p", "rb") as file:
            encodelistknown, studentids = pickle.load(file)
        safe_print("Encodings loaded.")
    except FileNotFoundError:
        safe_print("⚠️ Encoding file not found - face recognition will not work")
        encodelistknown, studentids = [], []
        FACE_RECOGNITION_AVAILABLE = False
else:
    safe_print("⚠️ Face recognition not available - skipping encoding load")
    encodelistknown, studentids = [], []

# ---------------- RESOURCES ----------------
try:
    imgBackground = cv2.imread("resources/background.png")
    foldermodepath = "resources/folders"
    if os.path.exists(foldermodepath):
        modepathlist = os.listdir(foldermodepath)
        imgmodellist = [cv2.imread(os.path.join(foldermodepath, path)) for path in modepathlist]
    else:
        safe_print("⚠️ Resources folder not found - creating dummy background")
        imgBackground = np.zeros((720, 1280, 3), dtype=np.uint8)
        imgmodellist = [np.zeros((666, 444, 3), dtype=np.uint8) for _ in range(4)]
except Exception as e:
    safe_print(f"⚠️ Error loading resources: {e}")
    imgBackground = np.zeros((720, 1280, 3), dtype=np.uint8)
    imgmodellist = [np.zeros((666, 444, 3), dtype=np.uint8) for _ in range(4)]

# ---------------- CAMERA ----------------
try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    safe_print("✅ Camera initialized")
except Exception as e:
    safe_print(f"⚠️ Camera initialization failed: {e}")
    cap = None

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

        imgBg = imgBackground.copy()
        imgBg[178:178 + 480, 61:61 + 640] = img
        imgBg[46:46 + 666, 810:810 + 444] = imgmodellist[modeType]

        if FACE_RECOGNITION_AVAILABLE:
            facecurrentFrame = face_recognition.face_locations(imgsmall)
            enccodecurrFrame = face_recognition.face_encodings(imgsmall, facecurrentFrame)

            if facecurrentFrame:
                for encodeface, faceloc in zip(enccodecurrFrame, facecurrentFrame):
                    matches = face_recognition.compare_faces(encodelistknown, encodeface)
                    facedistance = face_recognition.face_distance(encodelistknown, encodeface)
                    matchindex = np.argmin(facedistance)

                    if matches[matchindex]:
                        y1, x2, y2, x1 = faceloc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
                        imgBg = cornerRect(imgBg, bbox, rt=0)
                        id = studentids[matchindex]

                        if counter == 0:
                            putTextRect(imgBg, "Loading...", (905, 460), thickness=2)
                            counter = 1
                            modeType = 1
        else:
            # Basic face detection using OpenCV Haar cascades as fallback
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(imgsmall, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    # Scale back to original size
                    x, y, w, h = x * 4, y * 4, w * 4, h * 4
                    bbox = (55 + x, 162 + y, w, h)
                    imgBg = cornerRect(imgBg, bbox, rt=0)
                    putTextRect(imgBg, "Face Detected (No Recognition)", (905, 460), thickness=2)

        if counter != 0:
            if counter == 1:
                studentinfo = db.reference(f'Students/{id}').get()
                # blob = bucket.get_blob(f'Images/{id}.png')
                # array = np.frombuffer(blob.download_as_string(), np.uint8)
                # imgStudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                # what time should we choose to update another attendance record?

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


@app.route('/index')
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

    # Ensure images directory exists
    images_dir = os.path.join(os.getcwd(), 'images')
    os.makedirs(images_dir, exist_ok=True)

    original_name = secure_filename(file.filename)
    # default save name is original, but allow renaming by student_key
    requested_key = request.form.get('student_key') or request.args.get('student_key')
    if requested_key:
        # normalize key to safe filename (no path separators)
        key_safe = secure_filename(requested_key)
        _, ext = os.path.splitext(original_name)
        if not ext:
            ext = '.jpg'
        target_name = f"{key_safe}{ext}"
    else:
        target_name = original_name

    save_path = os.path.join(images_dir, target_name)
    try:
        file.save(save_path)
        safe_print(f"upload: saved file to {save_path}")
    except Exception as e:
        safe_print(f"upload: error saving file: {e}")
        return f"Error saving file: {e}", 500

    # Try upload to Firebase Storage (optional) only if bucket configured
    try:
        bucket_name = None
        try:
            # check app config first
            bucket_name = firebase_admin.get_app().options.get('storageBucket')
        except Exception:
            bucket_name = None

        # fallback to env var
        if not bucket_name:
            bucket_name = os.getenv('storagebucket') or os.getenv('STORAGE_BUCKET')

        if bucket_name:
            try:
                # prefer passing explicit bucket name
                bucket = storage.bucket(bucket_name)
                blob = bucket.blob(f"images/{target_name}")
                blob.upload_from_filename(save_path)
                safe_print(f"upload: uploaded to firebase storage images/{target_name}")
            except Exception as e:
                safe_print(f"upload: firebase storage upload failed: {e}")
        else:
            safe_print("upload: no firebase storage bucket configured; skipping cloud upload")
    except Exception as e:
        safe_print(f"upload: storage check failed: {e}")

    # 🔄 Update encodings (rebuild encoding file)
    try:
        update_encodings()
        safe_print("upload: encodings updated")
    except Exception as e:
        safe_print(f"upload: update_encodings failed: {e}")

    return redirect(url_for('upload_data_page'))



# ---------------- UPLOAD DATA FORM ----------------
@app.route('/upload_data')
def upload_data_page():
    return render_template('login.html')


@app.route('/student', methods=['GET', 'POST'])
def student_attendance():
    """Show a simple form where a student can enter their database key
    and see their attendance and (optionally) percentage when total
    number of classes is provided.
    """
    student = None
    percentage = None
    error = None

    if request.method == 'POST':
        key = request.form.get('student_key')
        total_classes_str = request.form.get('total_classes')

        if not key:
            error = 'Student key or official ID is required.'
            return render_template('student_attendance.html', error=error)

        try:
            # First try lookup by database key
            safe_print(f"Student lookup requested for input: '{key}'")
            student_ref = db.reference(f'Students/{key}')
            student = student_ref.get()

            # If not found, try searching by the official student 'id' field
            if not student:
                safe_print(f"No student at DB key '{key}', trying id lookup...")
                students_ref = db.reference('Students')
                normalized = key.strip()
                # Try exact query by child 'id'
                try:
                    query_result = students_ref.order_by_child('id').equal_to(normalized).get()
                except Exception as e:
                    query_result = None
                    safe_print(f"Warning: order_by_child query failed: {e}")

                if query_result:
                    # take the first matched student
                    first_key = next(iter(query_result))
                    student = query_result[first_key]
                    safe_print(f"Found student by id query under DB key '{first_key}'")
                else:
                    # Fallback: scan all students and compare normalized fields (case-insensitive)
                    try:
                        all_students = students_ref.get() or {}
                        found = None
                        lookup = normalized.lower()
                        for k, s in (all_students.items() if isinstance(all_students, dict) else []):
                            # check both 'id' and possibly 'student_unique_id' if present
                            sid = str(s.get('id', '')).strip().lower()
                            suid = str(s.get('student_unique_id', '')).strip().lower() if s.get('student_unique_id') else ''
                            if sid == lookup or suid == lookup:
                                found = s
                                break

                        if found:
                            student = found
                            safe_print("Found student by scanning all_students fallback")
                        else:
                            # Try matching ignoring leading zeros in stored id
                            lookup_nz = lookup.lstrip('0')
                            for k, s in (all_students.items() if isinstance(all_students, dict) else []):
                                sid = str(s.get('id', '')).strip().lower().lstrip('0')
                                if sid == lookup_nz:
                                    student = s
                                    break

                    except Exception as e:
                        safe_print(f"Error scanning students for fallback lookup: {e}")

                    if not student:
                        error = f'No student found for key or ID: {key}'
                        return render_template('student_attendance.html', error=error)

            # Ensure numeric attendance
            try:
                total_att = int(student.get('total_attendance', 0))
            except Exception:
                total_att = 0

            # Compute percentage if total_classes provided and > 0
            if total_classes_str:
                try:
                    total_classes = int(total_classes_str)
                    if total_classes > 0:
                        percentage = (total_att / total_classes) * 100
                    else:
                        percentage = None
                except ValueError:
                    percentage = None

            # Attach numeric values to template-friendly object
            student['total_attendance'] = total_att

        except Exception as e:
            error = f'Error reading database: {e}'

    return render_template('student_attendance.html', student=student, percentage=percentage, error=error)


@app.route('/add_firebase', methods=['POST'])
def add_firebase():
    try:
        student_id = request.form['student_id']
    except Exception as e:
        safe_print(f"add_firebase: missing student_id in form: {e}")
        return "Missing student_id", 400
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

    try:
        safe_print(f"add_firebase: adding student at key '{student_id}' with data: {data}")
        ref = db.reference("Students")
        ref.child(student_id).set(data)
        # Save uploaded image (if provided) into images/<student_id>.<ext>
        try:
            uploaded = request.files.get('image')
            if uploaded and uploaded.filename:
                images_dir = os.path.join(os.getcwd(), 'images')
                os.makedirs(images_dir, exist_ok=True)
                _, ext = os.path.splitext(uploaded.filename)
                ext = ext.lower() if ext else '.jpg'
                save_path = os.path.join(images_dir, f"{student_id}{ext}")
                uploaded.save(save_path)
                safe_print(f"add_firebase: saved uploaded image to {save_path}")
            else:
                safe_print("add_firebase: no image uploaded or filename empty")
        except Exception as e:
            safe_print(f"add_firebase: error saving uploaded image: {e}")

        safe_print("add_firebase: write succeeded")

        # Re-generate encodings (this will overwrite EncodeFileFaceRecognition.p)
        try:
            update_encodings()
            safe_print("add_firebase: encodings updated")
        except Exception as e:
            safe_print(f"add_firebase: error updating encodings: {e}")

        return "Data Uploaded Successfully!"
    except Exception as e:
        safe_print(f"add_firebase: write error: {e}")
        return f"Error writing to database: {e}", 500

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

    safe_print("✅ Encodings updated successfully.")

from flask import Flask , request,redirect , url_for , session, Response , render_template

@app.route('/login')
def login():
    return render_template("login.html")

@app.route("/submit",methods =["POST"])
def submit():
    username = request.form.get("username")
    password = request.form.get("password")

    # if username =="sohitpatel359" and password=="password":
    #     return render_template("welcome.html",name = username)

    validuser={
        'admin': '123',
        'preetiRai': 'preeti123',
        'sohit': 'Patel'
    }
    if username in validuser and password == validuser[username]:
        return render_template("upload_data.html",name = username)
    
    else:
        return render_template("login_failed.html")
    
# logout

@app.route('/logout')
def logout():
    return render_template("login.html")

@app.route('/index_log')
def index_log():
    return render_template('index_login.html')

@app.route("/submit_l",methods =["POST"])
def submit_l():
    username = request.form.get("username")
    password = request.form.get("password")

    # if username =="sohitpatel359" and password=="password":
    #     return render_template("welcome.html",name = username)

    validuser={
        'faculty': '123',
        'preetiRai': 'preeti123',
        'sohit': 'Patel'
    }
    if username in validuser and password == validuser[username]:
        return render_template("index.html",name = username)
    
    else:
        return render_template("index_log_fail.html")

@app.route("/")
def base_log():
    return render_template("base.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
