# Smart Attendance (Face Recognition)

A Python + Flask project for real-time face recognition attendance. The app captures faces from a webcam, recognizes students using precomputed encodings, and stores attendance data in Firebase Realtime Database. It also provides a simple web interface for uploading student data/images and checking attendance.

## Features

- Real-time face detection and recognition using OpenCV and face_recognition
- Stores student records and attendance counts in Firebase Realtime Database
- Simple web UI to stream camera feed, upload student data and images
- Student-facing page to check attendance by database key or official student ID
- Automatic encoding generation from images in `images/` (via `update_encodings()`)

## Repository layout

- `app.py` - Main Flask application and camera/recognition logic
- `templates/` - HTML templates (index, upload_data, student_attendance, ...)
- `static/` - Static assets (css, img, etc.)
- `images/` - Folder to hold student images (used to build face encodings)
- `EncodeFileFaceRecognition.p` - Pickled encodings file generated from `images/`
- `serviceAccountKey.json` - Firebase service account (DO NOT COMMIT to public repos)
- `adddatatodatabase.py` - Script that seeds students into Firebase (example data)
- `encodegenerater.py` / `update_encodings()` - Code that generates face encodings

## Requirements

The project requires Python 3.10+ (tested with 3.12). Install dependencies with:

```powershell
pip install -r requirements.txt
```

Key packages:
- Flask
- opencv-python
- face_recognition
- firebase-admin
- numpy

Note: Installing `dlib` and `face_recognition` may require build tools (CMake, Visual Studio Build Tools) on Windows. Use prebuilt wheels when possible.

## Setup

1. Clone the repository and create/activate a virtual environment:

```powershell
git clone <repo-url>
cd smart-attandance
python -m venv new_venv
.\new_venv\Scripts\activate.ps1
pip install -r requirements.txt
```

2. Firebase
- Create a Firebase project and Realtime Database.
- Generate a service account JSON and save it as `serviceAccountKey.json` in the project root. Keep this file private.
- Ensure your Realtime Database rules allow reads/writes for your testing setup, and add an index for the `id` field under `Students` (required for queries):

Example rules snippet (development/testing only):

```json
{
    "rules": {
        "Students": {
            ".indexOn": ["id"],
            ".read": true,
            ".write": true
        },
        ".read": true,
        ".write": true
    }
}
```

3. Environment variables
- Optionally create a `.env` and define `databaseurl` and `storagebucket` for Firebase. The app uses `python-dotenv` to load `.env`.

## Running the app

Run the Flask app directly:

```powershell
.\new_venv\Scripts\activate.ps1
python app.py
# or (if FLASK_APP is set): flask run
```

Open the web UI:
- Home (camera feed): `http://127.0.0.1:5000/` or `/index`
- Upload student data: `http://127.0.0.1:5000/upload_data`
- Student attendance check: `http://127.0.0.1:5000/student`

## How uploads work

- `upload_data.html` provides two forms:
    - Image-only upload (`/upload`) — saves the uploaded file to `images/` (optionally renamed using a provided student key) and regenerates encodings.
    - Student-data form (`/add_firebase`) — saves student metadata to Firebase and will save any uploaded image to `images/<student_key>.<ext>` and call `update_encodings()`.

- When `update_encodings()` runs, it reads images from `images/`, computes face encodings, and writes `EncodeFileFaceRecognition.p`.

## Student lookup

- The `/student` page accepts either the Firebase DB key (e.g., `133`) or the official enrollment ID (e.g., `0206AL231133`). The server first looks up `Students/<key>`, then tries a query by `id`, and finally falls back to scanning entries when indexing isn't available.

Important: Add `".indexOn": ["id"]` under `Students` in your DB rules to support efficient order_by_child('id') queries.

## Troubleshooting

- Internal Server Error when uploading images:
    - Check Flask console for the exact exception. Common issues: missing `opencv-python`, Firebase Storage bucket not configured.
    - If you don't use Firebase Storage, the app will still save images locally under `images/` and continue.

- face_recognition / dlib install failures:
    - On Windows, install Visual Studio Build Tools and CMake, or use prebuilt binary wheels for `dlib`.

- Encodings not updated:
    - Confirm `images/` contains valid face photos and `update_encodings()` completes successfully. If face_recognition cannot find a face in an image, it may error.

## Development notes

- Logging: `safe_print()` is used to avoid Unicode console errors on Windows terminals.
- The app is intended for development/demo use. Consider the following improvements for production:
    - Run the Flask app under a production WSGI server (Gunicorn/Waitress).
    - Protect Firebase credentials and tighten Realtime Database rules.
    - Run `update_encodings()` asynchronously (celery/background thread) to avoid blocking uploads.

