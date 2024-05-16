from ultralytics import YOLO
from picamera2 import Picamera2
import tinytuya
import Adafruit_DHT as dht
import time
import firebase_admin
from firebase_admin import credentials, db
from ultralytics.utils.plotting import Annotator
import cv2
import requests

cred = credentials.Certificate("humi-f17e6-firebase-adminsdk-zvdy8-291529a94d.json")
firebase_admin.initialize_app(cred, {'databaseURL' : 'https://humi-f17e6-default-rtdb.firebaseio.com/'})
table = db.reference('humidity')

d = tinytuya.OutletDevice('1300760684f3ebdeacf6', '192.168.0.115', '!%ndMS@m}t5kw8J?')
d.set_version(3.3)

picam2 = Picamera2()
picam2.preview_configuration.main.size = (800,800)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

model = YOLO("yolov8n.pt")
count = 0
counth = 0
counts = 1
STATUS = ''
while True:
    humidity, temperature = dht.read_retry(dht.DHT22,4)
    table.update({counth : humidity})
    table.update({counts : STATUS})
    counth = counth + 2
    counts = counts + 2
    img = picam2.capture_array()
    results = model(img)
    if list(results[0].boxes.cls.detach().numpy()).count(0)>0:
       
        annotator = Annotator(img)
        boxes = results[0].boxes
        for box in boxes:
           
            b = box.xyxy[0]
            c = box.cls
            if c == 0 :
                annotator.box_label(b, model.names[int(c)])

        img = annotator.result()
        _, buffer = cv2.imencode('.jpg', img)
        requests.post("http://8867-1-233-65-186.ngrok-free.app/image_save", files = {"frame" : buffer.tobytes()})
        # cv2.imshow('YOLO V8 Detection', img)
        if humidity < 50 :
            d.turn_on()
            STATUS = 'ON'
            print(f'current humidity : {humidity}%',f'- HUMIDIFIER STATUS : {STATUS}')        
            count = 0
    else :
        count = count + 1
       
    if count > 2 :
        d.turn_off()
        STATUS = 'OFF'
        print(f'no people detected - HUMIDIFIER STATUS : {STATUS}')
        count = 0
    if cv2.waitKey(1) == ord('q'):
        break
    time.sleep(10)