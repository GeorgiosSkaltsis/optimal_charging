import datetime
import math
import random
import uuid

import requests
import pickle
import numpy as np
import json

random.seed(42)
baselink = 'http://160.40.51.98:8080/cim/repository/cim'
event_link = '/setEvent'
get_event_link = '/getEvent'
get_events_by_type_link = '/getEventsByType'
delete_event_link = '/deleteEvent'
get_user_link = '/getUser'
get_users_link = '/getUsers'
id = str(uuid.uuid4())


def get_event(identity = id):
    PARAMS = {'lfmName': 'defaultmarket', 'eventId': identity}

    # sending get request and saving the response as response object
    r = requests.get(url=baselink + get_event_link, params=PARAMS)

    # extracting data in json format
    data = r.json()
    # print(data)
    return data

def get_events_by_type(start_date, end_date, type = 'FlexibilityForecastAsset'):
    PARAMS = {'lfmName': 'defaultmarket', 'type': type, 'startDateTime':start_date, 'endDateTime': end_date}

    # sending get request and saving the response as response object
    r = requests.get(url=baselink + get_events_by_type_link, params=PARAMS)

    # extracting data in json format
    data = r.json()
    return data
#     <baseURL>/getEventsByType?lfmName=defaultmarket
# &eventType=GridNetworkStatus
# &startDateTime=2020-01-10T13:00:00
# &endDateTime=2020-03-10T14:00:00

def post_flexibility( data ): # data is already json-ized or in a form of a dictionary.
    # Serializing json
    json_object = json.dumps(data)# , indent=4
    # sending post request and saving response as response object
    r = requests.post(url=baselink + event_link, data=json_object)

    # extracting response text
    pastebin_url = r.text
    print("The pastebin URL is:%s" % pastebin_url)

def delete_event(identity = id):
    data = {
        'lfmName': 'defaultmarket',
        'eventId': identity
    }
    # Serializing json
    json_object = json.dumps(data, indent=4)
    print(json_object)
    # sending post request and saving response as response object
    r = requests.post(url=baselink + delete_event_link, data=json_object)

    # extracting response text
    pastebin_url = r.text
    print("The pastebin URL is:%s" % pastebin_url)

def get_user(identity = id):
    PARAMS = {'lfmName': 'defaultmarket', 'userId': identity}

    # sending get request and saving the response as response object
    r = requests.get(url=baselink + get_user_link, params=PARAMS)

    # extracting data in json format
    data = r.json()
    # print(data)
    return data


def get_users():
    PARAMS = {'lfmName': 'defaultmarket'}

    # sending get request and saving the response as response object
    r = requests.get(url=baselink + get_users_link, params=PARAMS)

    # extracting data in json format
    data = r.json()
    # print(data)
    return data
