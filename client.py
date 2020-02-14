import serial
import sys
import time
import requests
import threading
import datetime

alarms = []
medicines = []

class Alarm:
    def __init__(self, id, name, hours, medicine_ids, device_id, contacts):
        self.id = id
        self.name = name
        self.hours = hours
        self.medicine_ids = medicine_ids
        self.device_id = device_id
        self.contacts = contacts
    def __repr__(self):
        return self.hours + ' ' + self.name

class Medicine:
    def __init__(self, id, name, quantity, dosage, device_id):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.dosage = dosage
        self.device_id = device_id
    def __repr__(self):
        return self.name

def getDataAsJson(url):
    r = requests.get(url)
    data = r.json()
    return data

def getAlarmsFromJson(json):
    alarms = []
    for alarm in json:
        alarms.append(Alarm(alarm['id'], alarm['name'], alarm['hours'], alarm['medicine_ids'], alarm['device_id'], alarm['contacts']))
    return alarms

def getMedicinesFromJson(json):
    medicies = []
    for medicine in json:
        medicies.append(Medicine(medicine['id'], medicine['name'], medicine['quantity'], medicine['dosage'], medicine['device_id']))
    return medicies

def getAlarmsAndMedicines():
    global alarms
    global medicines
    alarm_json = getDataAsJson("https://api.epilulier.fr/alarm")
    medicine_json = getDataAsJson("https://api.epilulier.fr/medicine")
    alarms = getAlarmsFromJson(alarm_json)
    medicines = getMedicinesFromJson(medicine_json)
    threading.Timer(2.0, getAlarmsAndMedicines).start()

def postSignal(alarm_id):
    url = "https://api.epilulier.fr/signal"
    data = {'alarm_id': alarm_id}

    requests.post(url = url, data = data)

def deleteSignal(alarm_id):
    url = "https://api.epilulier.fr/signal"
    data = {'alarm_id': alarm_id}

    requests.delete(url = url, data = data)

def patchSignal(alarm, medicines):
    medicine_ids = alarm.medicine_ids.split()
    base_url = "https://api.epilulier.fr/medicine/"

    for item in medicine_ids:
        url = base_url + item
        for med in medicines:
            if med.id == int(item):
                data = {'name': med.name, 'quantity': med.quantity - med.dosage, 'dosage': med.dosage}
                requests.patch(url, data)
                return

try:
    getAlarmsAndMedicines()
    serial_port = serial.Serial(port='COM3', baudrate=9600, timeout=0)
except serial.SerialException:
    print("Could not open port")
    sys.exit(84)
except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(84)

waiting_alarm = None
delivered_ids = []

while 1:
    if serial_port.in_waiting > 0:
        buffer = serial_port.read()
        if buffer == '1' and waiting_alarm != None:
            deleteSignal(waiting_alarm.id)
            patchSignal(waiting_alarm, medicines)
            waiting_alarm = None
    for alarm in alarms:
        split = alarm.hours.split(':')
        if len(split) > 1:
            if int(split[0]) == datetime.datetime.now().hour and int(split[1]) == datetime.datetime.now().minute and alarm.id not in delivered_ids:
                serial_port.write('2')
                postSignal(alarm.id)
                waiting_alarm = alarm
                delivered_ids.append(alarm.id)
                print("Delivered.")
    time.sleep(1)
