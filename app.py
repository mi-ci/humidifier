from flask import Flask, render_template, request, Response, redirect, jsonify, send_file
import random
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime

cred = credentials.Certificate("humi-f17e6-firebase-adminsdk-zvdy8-2d96502cac.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://humi-f17e6-default-rtdb.firebaseio.com'
})
table = db.reference('humidity')

global size
size = 0

app = Flask(__name__)
@app.route('/')
def main():
    global size
    return render_template('main.html', size=size)

@app.route("/get_data", methods=["POST"])
def get_data():
    
    data = table.get()
    humidity = data[-2]
    humidity = int(humidity)
    status = data[-1]

    page = requests.get("https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query=%EC%B2%9C%ED%98%B8%EB%8F%99+%EB%82%A0%EC%94%A8")
    soup = bs(page.text, "html.parser")
    elements = soup.select('div.temperature_info')
    out_humidity = str(elements[0]).split('%')[0][-2:]

    return jsonify({"out_humidity": out_humidity, "humidity": humidity, "size" : size, 'status' : status})




@app.route('/image_save', methods=['POST'])
def image_save():
    img_bytes = request.files['frame'].read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    global size
    save_to = f'static/image/image{size}.jpg'
    size = size + 1
    cv2.imwrite(save_to,img)
    print("image saved~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)