#!/usr/bin/env python

import urllib.request, urllib.parse
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
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooShoppingSearch":
        return {}
    baseurl = "https://shopping.yahooapis.jp/ShoppingWebService/V1/json/itemSearch?"
    param = makeRequestParameter(req)
    if param is None:
        return {}
    request_url = baseurl + urllib.parse.urlencode(param)
    print(request_url)

    result = urllib.request.urlopen(request_url).read()
    print("result: ")
    print(result)

    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeRequestParameter(req):
    result = req.get("result")
    parameters = result.get("parameters")
    query = parameters.get("query")
    appid = parameters.get("appid")
    if (query is None) or (appid is None):
        return None

    parameter = {"appid":appid,
                 "query":query,
                 "hits":1}

    return parameter


def makeWebhookResult(data):
    result_set = data.get('ResultSet')
    if result_set is None:
        return {}

    result = result_set.get('0')
    result = result.get('Result')
    if result is None:
        return {}

    hit = result["0"]
    if hit is None:
        return {}

    name = hit.get('Name')
    headline = hit.get('Headline')
    if (name is None) or (headline is None):
        return {}

    speech = name + "、の商品が見つかりました"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-yshp-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
