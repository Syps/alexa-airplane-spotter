from __future__ import print_function
from lambda_settings import app_id, speech_endpoint
import requests
import json

def is_valid_app(event):
    return event['session']['application']['applicationId'] == app_id

def get_output_speech():
    r = requests.get(speech_endpoint)
    output = json.loads(r.text)['response'].encode('ascii')
    return output

def get_response():
    return {
          "version": "1.0",
          "response": {
            "outputSpeech": {
              "type": "PlainText",
              "text": get_output_speech()
              },
            "card": {
              "content": "Planes rule!",
              "title": "Plane Info",
              "type": "Simple"
            },
            "reprompt": {
              "outputSpeech": {
                "type": "PlainText",
                "text": ""
              }
            },
            "shouldEndSession": 'false'
          },
          "sessionAttributes": {}
        }

def lambda_handler(event, context):
    if not is_valid_app(event):
        print(event['session']['application']['applicationId'])
        raise ValueError('Invalid Application ID')

    return get_response()
