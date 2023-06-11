import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import shutil
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

app = FastAPI()  # create a new FastAPI app instance

# port = int(os.getenv("PORT"))
port = 8080

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"


def uploadtogcs(filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket("eduwaste")
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    return blob.public_url


def updatedata(userID, url):
    cred = credentials.Certificate("service_account.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection("user").document()
    temp = datetime.now()
    doc_ref.set(
        {"userID": userID, "url": url, "date": temp.strftime("%d/%m/%Y %H:%M:%S")}
    )
    return "success"


# model = tf.saved_model.load('./tf2-save', signatures={
#         tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY: concrete_funct})


# def predict(location):
#     img = image.load_img(location, target_size=(64,64))
#     test_image = image.img_to_array(img)
#     test_image = np.expand_dims(test_image, axis = 0)
#     result = model.predict(test_image)
#     prediction = ''
#     if result[0][0] == 1:
#         prediction = 'Recyclable'
#     else:
#         prediction = 'Organic'
#     return prediction


@app.get("/")
def hello_world():
    return "hello world"


@app.post("/uploadtogcs")
def upload(input: UploadFile = File(...)):
    print(input.filename)
    print(type(input.filename))
    savefile = input.filename
    with open(savefile, "wb") as buffer:
        shutil.copyfileobj(input.file, buffer)
    result = uploadtogcs(savefile)
    os.remove(savefile)
    return str(result)


@app.post("/updatedata")
def updatefsdata(userID: str = Form(...), url: str = Form(...)):
    result = updatedata(userID, url)
    return str(result)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=1200)
