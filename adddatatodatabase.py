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
    "133":{
        "name":"Sohit Patel",
        # "branch":"Branch: AIML",
        "branch":"AIML",
        # "year":"Year: 3rd",
        "year":"5th",
        # "graduate_year":"Passing Year: 2027",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:54:54",
        "id":"0206AL231133",
        "standing_year":"B"
        

    },
    "11":{
        "name":"Aditya Chouksey",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231011",
        "standing_year":"B"
        

    },
    "60":{
        "name":"Dovari Abhishek",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231060",
        "standing_year":"B"
        

    },
    "66":{
        "name":"Inderaneela Sarkar",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231066",
        "standing_year":"B"
        

    },
    "66":{
        "name":"Ishita Sharma",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231068",
        "standing_year":"B"
        

    },
    "83":{
        "name":"Mayank Mehra",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231083",
        "standing_year":"B"
        

    },
    "84":{
        "name":"M.Hassan Khan",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231084",
        "standing_year":"B"
        

    },
    "86":{
        "name":"Muskan Barekar",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231086",
        "standing_year":"B"
        

    },
    "88":{
        "name":"Nidhi Soni",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231088",
        "standing_year":"B"
        

    },
    "94":{
        "name":"Palak Gurjar",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231094",
        "standing_year":"B"
        

    },
    "95":{
        "name":"Palak Patel",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231095",
        "standing_year":"B"
        

    },
    "96":{
        "name":"Pankaj Bairwa",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231096",
        "standing_year":"B"
        

    },
    "97":{
        "name":"Piyush Namdeo",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231097",
        "standing_year":"B"
        

    },
    "101":{
        "name":"Pratha Jain",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231101",
        "standing_year":"B"
        

    },
    "103":{
        "name":"Rajan Mishra",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231103",
        "standing_year":"B"
        

    },
    "105":{
        "name":"Rakshan Tiwari",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231105",
        "standing_year":"B"
        

    },
    "106":{
        "name":"Rishi Saraswat",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231106",
        "standing_year":"B"
        

    },
    "107":{
        "name":"Rishi Sharma",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231107",
        "standing_year":"B"
        

    },
    "109":{
        "name":"Riyanshi Sengupta",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231109",
        "standing_year":"B"
        

    },
    "111":{
        "name":"S Anubhav Singh",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231111",
        "standing_year":"B"
        

    },
    "114":{
        "name":"Samarth Choubey",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231114",
        "standing_year":"B"
        

    },
    "116":{
        "name":"Sameer Rawat",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231116",
        "standing_year":"B"
        

    },
    "119":{
        "name":"Sankalp Lakhera",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231119",
        "standing_year":"B"
        

    },
    "126":{
        "name":"Shriya Kumari",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231126",
        "standing_year":"B"
        

    },
    "131":{
        "name":"Smriti Kumari",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231131",
        "standing_year":"B"
        

    },
    "136":{
        "name":"Sumit Bhandari",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231136",
        "standing_year":"B"
        

    },
    "138":{
        "name":"Suyash Tiwari",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231138",
        "standing_year":"B"
        

    },
    "140":{
        "name":"Tanisha Shukla",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231140",
        "standing_year":"B"
        

    },
    "146":{
        "name":"Ujjwal Sahu",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231146",
        "standing_year":"B"
        

    },
    "147":{
        "name":"Ujjwal Thakur",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231147",
        "standing_year":"B"
        

    },
    "153":{
        "name":"Yash Parihar",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231153",
        "standing_year":"B"
        

    },
    "155":{
        "name":"Yuvika Koshta",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231155",
        "standing_year":"B"
        

    },
    "156":{
        "name":"Yuvraj Lodhi",
        "branch":"AIML", 
        "year":"5th",
        "graduate_year":"2027",
        "total_attendance":0,
        "last_attendance":"2025-10-15 00:34:14",
        "id":"0206AL231156",
        "standing_year":"B"
        

    },
    
    
}
for key, value in data.items():
    ref.child(key).set(value)