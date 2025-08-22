import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://faceattendancerealtime-93ab5-default-rtdb.firebaseio.com/"
})


ref = db.reference("Students")

data = {
    "0123":{
        "name":"Sohit Patel",
        "branch":"Branch: AIML",
        "year":"Year: 3rd",
        "graduate_year":"Passing Year: 2027",
        "total_attendance":8,
        "last_attendance":"2025-3-23 00:54:54",
        

    },
    "1234":{
        "name":"Narendra Modi",
        "branch":"Branch: CS", 
        "year":"Year: 4th",
        "graduate_year":"Passing Year: 2026",
        "total_attendance":3,
        "last_attendance":"2025-1-23 00:34:14",
        

    },
    "5678":{
        "name":"Allu Arjun",
        "branch":"Branch: CSBS",
        "year":"Year: 1st",
        "graduate_year":"Passing Year: 2028",
        "total_attendance":16,
        "last_attendance":"2025-2-23 00:12:44",
        

    },
}
for key, value in data.items():
    ref.child(key).set(value)