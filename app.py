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
    if req.get("result").get("action") == "yahooShoppingSearch":
        r = Search(req)
    elif req.get("result").get("action") == "yahooShoppingRankingAll":
        r = RankingAll(req)
    elif req.get("result").get("action") == "yahooShoppingRankingCategory":
        r = RankingCategory(req)
    else:
        return {}

    return r.res


class YahooShopping(object):

    def __init__(self, req):
        param = self.parseParameter(req)
        request_url = self.generateRequestUrl(param)
        result = urllib.request.urlopen(request_url).read()
        data = json.loads(result)
        self.res = self.makeWebhookResult(data)

    def parseParameter(self, req):
        pass

    def generateRequestUrl(self, param):
        pass

    def makeWebhookResult(self, data):
        pass


class Search(YahooShopping):

    def parseParameter(self, req):
        result = req.get("result")
        parameters = result.get("parameters")
        appid = parameters.get("appid")
        query = parameters.get("query")
        if (appid is None) or (query is None):
            return None

        parameter = {"appid":appid,
                     "query":query,
                     "hits":1}

        return parameter

    def generateRequestUrl(self, param):
        baseurl = "https://shopping.yahooapis.jp/ShoppingWebService/V1/json/itemSearch?"
        request_url = baseurl + urllib.parse.urlencode(param)
        return request_url

    def makeWebhookResult(self, data):
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
        if (name is None):
            return {}

        speech = name + "、の商品はいかがですか"

        return {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-yshp-webhook"
        }


class RankingAll(Search):

    def parseParameter(self, req):
        result = req.get("result")
        parameters = result.get("parameters")
        appid = parameters.get("appid")
        if (appid is None):
            return None

        parameter = {"appid":appid}

        return parameter

    def generateRequestUrl(self, param):
        baseurl = "https://shopping.yahooapis.jp/ShoppingWebService/V1/json/categoryRanking?"
        request_url = baseurl + urllib.parse.urlencode(param)
        return request_url


class RankingCategory(Search):

    def parseParameter(self, req):
        result = req.get("result")
        parameters = result.get("parameters")
        appid = parameters.get("appid")
        if (appid is None):
            return None

        parameter = {"appid":appid}

        for key in ["category_id", "gender", "generation", "type"]:
            val = parameters.get(key)
            if val:
                parameter[key] = val

        return parameter

    def generateRequestUrl(self, param):
        baseurl = "https://shopping.yahooapis.jp/ShoppingWebService/V1/json/categoryRanking?"
        request_url = baseurl + urllib.parse.urlencode(param)
        return request_url


class Sample(RankingAll):

    def __init__(self):
        param = {"appid":""}
        request_url = self.generateRequestUrl(param)
        result = urllib.request.urlopen(request_url).read()
        data = json.loads(result)
        self.res = self.makeWebhookResult(data)


if __name__ == '__main__':
    #r = Sample()
    #print(r.res)

    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
