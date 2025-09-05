import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('databaseurl'),
    # 'storageBucket': os.getenv('storagebucket')
})


ref = db.reference("Students")

data = {
    "0123":{
        "name":"Sohit Patel",
        # "branch":"Branch: AIML",
        "branch":"AIML",
        # "year":"Year: 3rd",
        "year":"3rd",
        # "graduate_year":"Passing Year: 2027",
        "graduate_year":"2027",
        "total_attendance":8,
        "last_attendance":"2025-3-23 00:54:54",
        "id":"0206AL231133",
        "standing_year":"B"
        

    },
    "1234":{
        "name":"Narendra Modi",
        "branch":"CS", 
        "year":"4th",
        "graduate_year":"2026",
        "total_attendance":3,
        "last_attendance":"2025-1-23 00:34:14",
        "id":"0206AL231134",
        "standing_year":"A"
        

    },
    "5678":{
        "name":"Allu Arjun",
        "branch":"CSBS",
        "year":"1st",
        "graduate_year":"2028",
        "total_attendance":16,
        "last_attendance":"2025-2-23 00:12:44",
        "id":"0206AL231135",
        "standing_year":"D"
        

    },
    "8765":{
        "name":"Gandhi JI",
        "branch":"Nark",
        "year":"Died",
        "graduate_year":"1949",
        "total_attendance":50,
        "last_attendance":"2025-4-23 00:54:54",
        "id":"0206AL231136",
        "standing_year":"C"
    }
}
for key, value in data.items():
    ref.child(key).set(value)