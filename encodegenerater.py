import cv2
import face_recognition
import pickle
import os
import firebase_admin


# importing images list
folderpath = "images"
pathlist = os.listdir(folderpath)
# print(pathlist)
imglist = []
studentids = []
for path in pathlist:
    imglist.append(cv2.imread(os.path.join(folderpath,path))) #folder of modes   
    studentids.append( os.path.splitext(path)[0]) #remove .jpg from image
    # print(path)
    # print( os.path.splitext(path)[0])

    filename = f'{folderpath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)

print(studentids)


def findencoding(imglist):
    encodelist=[]
    for img in imglist:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodelist.append(encode)

    return encodelist
print("Encoding begin.... ")
encodelistknown = findencoding(imglist)
encodelistknownIds = [encodelistknown,studentids]
print("Encoding Complete ")

file = open("EncodeFileFaceRecognition.p",'wb')
pickle.dump(encodelistknownIds,file)
file.close()
print("file saved")