#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    
    if req.get("result").get("action").startswith("smalltalk"):
        speech = req.get("result").get("fulfillment").get("messages").get("speech")
        return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-EULA-webhook-sample"
        }
    
    if req.get("result").get("action") == "FetchEULA":
        request = makeEULAQuery(req)
        if request is None:
            return {}

        result = urlopen(request).read()
        data = json.loads(result)
        res = makeEULAResult(data)
        return res
    elif req.get("result").get("action") == "LatchDoor":
        
        print("LatchDoor entry")
        
        request = makeDoorLatchQuery(req)
        
        if request is None:
            return {}
        
        print("Before url open")

        result = urlopen(request).read()
        
        print("After url open")
        
        data = json.loads(result)
        
        print("Result:")
        print(data)
        
        res = makeDoorLatchResult(data)
        
        print(res)
        
        return res
    else:
        return {}
    
def makeDoorLatchQuery(req):    
    
    print("makeDoorLatchQuery entry")
    
    baseurl = "https://isom.beta.mymaxprocloud.com/ISOM/ISOM/DeviceMgmt/Doors/"
    result = req.get("result")
    parameters = result.get("parameters")
    state = parameters.get("state")
    doorId = parameters.get("doorId")
    cred = parameters.get("credential")
   
    if state is None:
        return None
    
    request = Request(
        baseurl + doorId + "/latchState/" + state,
        headers={"Authorization" : ("Basic %s" % cred)}
    )
    return request
   
def makeEULAQuery(req):    
    baseurl = "https://isom.beta.mymaxprocloud.com/ISOM/Custom/MPCEula/config?"
    result = req.get("result")
    parameters = result.get("parameters")
    prod = parameters.get("productName")
    cred = parameters.get("credential")
    
    if prod is None:
        return None
    
    request = Request(
        baseurl + "q=(ProductName=" + prod + ")",
        headers={"Authorization" : ("Basic %s" % cred)}
    )
    return request

def makeEULAResult(data):
    print("makeWebhookResult entry")
    first = data.get('mpcEulaConfig')[0]
    if first is None:
        return {}

    productName = first.get('mpcProductName')
    if productName is None:
        return {}

    print(productName)
    
    createdDateTime = first.get('createdDateTime')
    if createdDateTime is None:
        return {}

    print(createdDateTime)
    
    text = first.get('text')
    
    if text is None:
        return {}

    text = "HONEYWELL MAXPRO CLOUD HOSTED SERVICES END USER LICENSE AGREEMENT [truncated]..."
    
    speech = "EULA for " + productName + " created on  " + createdDateTime + " is : " + text 

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-EULA-webhook-sample"
    }

def makeDoorLatchResult(data):
    print("makeDoorLatchResult entry")

    statusCode = data.get('statusCode')
    if statusCode is None:
        return {}

    print(statusCode)
    
    statusString = data.get('statusString')
    if statusString is None:
        return {}

    print(statusString)

    speech = "Status code = " + statusCode + ", Status String =  " + statusString

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-Latch-webhook-sample"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
