#s
# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
print("ss")
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import pandas
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
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    #baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    #speech = yql_query
    print(yql_query)
    if yql_query is None:
        return {}
    #yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    #result = urlopen(yql_url).read()
    #query_job = client.query(yql_query)
    #print("Response:")
    #print(speech)
    #res =  { "speech": speech,
    #    "displayText": speech,
    #         "source": "apiai-weather-webhook-sample"
    #        }
    #return res
    try:
        query_job = pandas.read_gbq(str(yql_query),
                                 project_id=credential['project_id'], index_col=None, col_order=None,
                                 reauth=False, verbose=True, private_key=json.dumps(credential), dialect='standard')
        #query_job = "nitin"
        query_job = query_job.ix[0,0]
    except Exception as e :
        query_job = "ERROR"
    #query_job = str(yql_query) + str(credential['project_id'] ) + str(json.dumps(credential))
    res =  { "speech": query_job,
        "displayText": query_job,
             "source": "apiai-weather-webhook-sample"
            }
    return res
    #rows = query_job.result()
    #for row in rows:
    #    data = (row)[0]
    #data = query_job.ix[0,0]
    #data = json.loads(result)
    #return { "speech": data,
    #    "displayText": data
     #       }
    #res = makeWebhookResult(data,req)
    #return res


def makeYqlQuery2(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city.upper() + "')"

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    #return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"
    #return city
    return "SELECT count(*) FROM `bigquery-public-data.irs_990.irs_990_ein`"
    #return  "SELECT count(*) FROM `bigquery-public-data.irs_990.irs_990_ein` WHERE city = '" + city + "'"
    #return 'SELECT count(*) FROM `bigquery-public-data.irs_990.irs_990_ein`'
            #'WHERE city = "SUNNYVALE" '
            # 'LIMIT 2'



def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Hi Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    
    credential = {
  "type": "service_account",
  "project_id": "thinking-text-180509",
  "private_key_id": "15ff34e6d5d187fcdc774bdae8695f47241d7827",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQChF1Yhrlvcnqt8\nvpRzDPDZatQlmU9K5kkzValoYDw2dEbjR3Y4SMbqI2odIiRquBsw1DBH+C+ewD5s\nvYjNg4hrhw7NvMUAUoS2GtS9w8ayaTbV99k5OdUgGm5SgSTXuw9yyzLCQ7Mmlpks\nFof3cWZ+NPyHu/otWX4dzfOQ3vhHmuLA0lSVEvbn01z/GKhnDGiYNF87WNOIUZLK\nNxsdgAFVTxHb3ldi0RCWuQuSwRLtDGBSEyZfMGT62j7gLNoMrR6fBXnJMKhSLro4\n2kdrSsjN+C4OZgBRU+ebLQVueElM+cODlyxSRVIqemg6RqnolFGEKRjnmFdsVu8S\n/QHgx6cjAgMBAAECggEACRXl3EtOEDHz68zuMeb5zWlnC/2LBMK2iQ7zfjRocPrx\n5bhFO4ST2lTH3MjId+Iff53O803nTRf8Ww5Gs4nGwfCmG6q9nkGbeyHcRUH0nz0Z\nn4KjXXvBQJ+z3A4/df7SCju1Ygk9vbu0sr8DtwME52jHWx9RAlLrQSunDfWJ/P2D\nkWSlRvPrUkvO+2hBC/iiFJfODMJJQBBQtmilQCnKN/AEAemrias6s/4s+2BdlGIj\nRDmfHNOQHjMpzqA13INyE3OMaMIi1jnke0QJ4+Kr4dcrGztSVjPETBzxmDEphZYO\ncUiudCu9MsOq2pbQAqgjCufFgTq6+Yho7Tt4R8BMAQKBgQDSJEKXwzp7APCqHBXl\nWqI1pCKWnN1gTV78zpdIqBvrL42H6T5JlHSaeXe5/XJ/JOfO6HfGdZE9DgKZvxoi\nllClctG3BMokRXZWojDXZGx+1J4irFrOr4RBOeX/FJrdzngHhlRTXId8R/YnPao/\nDg+6/2jaL2xT+8gwY/KqgG/gIwKBgQDEPtRqY9vtjOjS4RW6JeJ32aPvNOOOI0V7\n+HudDbU2JOOO/6sN/Yrg5911kcU9g0KIJXRHisUGSCfEWYwklW/ncxb6h2UtsExl\nNchJWJ0zrUXBXf9AfIXibPw50hXQ+cHTixqyE5Gc61dwsrmkg3qs06tXDIhUwD9r\n9EqbipINAQKBgFdEV6NOn+qU6Vy7bRxiFxrPns2NNyHW/6tc39Z8eZuhk9TtN8C2\ntfWwm9fROMs0OE/kmlkAWeBRASN4CRJz+em7VPv8MTX+4rX3hPDt82B4S3N6v/s1\nSGcN9EWJ+QZDx/TYBAzaUCl8eOyy3xBwdnfhuVlieEooNWpjF1NXIx6hAoGAMl6B\n/LCWwTj6hS26euXAY8ybtAjaIyBQdEpJx/y9tyDuu0RJ7jRWUfWRNNzuSCSJjhI2\n7ynh+gPJGS92tekZKMm0aycXRAvM/+k2+ARjjOD7V2891ZpgbsZUUq7mZJXGNvqs\nJmq5ZBJPhiCJX31TnkpR3uzbjQ0u+hFgmN2PMQECgYAbAkgsrDqN7dMnby7Oqmwi\nXDjhuunEAXCcgLiVX6DUXAFvHImxytBFubscHdlPhy+Xy7UPa52+WSCdNaKN0HIL\n6+dbhu1xgdf/J6zC8pmjlNcSHsr/JDOzjxso/RQpLNVoUY61BnMWomZi0Ivkm3dF\n12tU661Q7Ar6X5FeHRE+ZQ==\n-----END PRIVATE KEY-----\n",
  "client_email": "bigquery@thinking-text-180509.iam.gserviceaccount.com",
  "client_id": "111452959638693076451",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bigquery%40thinking-text-180509.iam.gserviceaccount.com"
}
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
