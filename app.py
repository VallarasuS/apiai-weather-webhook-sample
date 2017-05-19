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

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "FetchEULA":
        return {}

    request = makeYqlQuery(req)
    if request is None:
        return {}

    result = urlopen(request).read()
    data = json.loads(result)
    print(data)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):    
    baseurl = "https://isom.beta.mymaxprocloud.com/ISOM/Custom/MPCEula/config?"
    result = req.get("result")
    parameters = result.get("parameters")
    prod = parameters.get("productName")
    print(prod)
    cred = parameters.get("credential")
    print(cred)
    if prod is None:
        return None
    
    request = Request(
        baseurl + "q=(ProductName=" + prod + ")",
        headers={"Authorization" : ("Basic %s" % cred)}
    )
    return request


def makeWebhookResult(data):
    first = data.get('mpcEulaConfig')
    if first is None:
        return {}

    productName = first.get('mpcProductName')
    if productName is None:
        return {}

    createdDateTime = first.get('channel')
    if createdDateTime is None:
        return {}

    text = first.get('text')

    # print(json.dumps(item, indent=4))

    speech = "EULA for " + productName + " created on  " + createdDateTime + " is : " + text 

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-EULA-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
