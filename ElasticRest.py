import http.client
import json
import datetime
import pytz
import uuid

ELASTIC_URL = 'localhost'
ELASTIC_PORT = '9200'


def bulk():
    pload = '''{ "index" : { "_index" : "test", "_id" : "1" } }
    { "field1" : "value1" }
    { "delete" : { "_index" : "test", "_id" : "2" } }
    { "create" : { "_index" : "test", "_id" : "3" } }
    { "field1" : "value3" }
    { "update" : {"_id" : "1", "_index" : "test"} }
    { "doc" : {"field2" : "value2"} }'''
    r = requests.post(ELASTIC_URL+'test/_bulk', data = pload)
    print(r.text)


def insert(index, id, doc):

    conn = http.client.HTTPConnection(ELASTIC_URL, ELASTIC_PORT)

    headers = {'Content-type': 'application/json'}
    json_data = json.dumps(doc)

    conn.request('PUT', '/{}/_doc/{}'.format(index, id), json_data, headers)
    response = conn.getresponse()
    if response.status not in [200, 201]:
        print("ERROR: Status: {} and reason: {}".format(response.status, response.reason))
    #print("Headers: {}".format(response.getheaders()))
    #print("Response: {}".format(response.read().decode()))
    conn.close()


def status():
    conn = http.client.HTTPConnection(ELASTIC_URL, ELASTIC_PORT)
    conn.request("GET", "/")
    response = conn.getresponse()
    print("Status: {} and reason: {}".format(response.status, response.reason))
    print("Headers: {}".format(response.getheaders()))
    print("Response: {}".format(response.read().decode()))
    conn.close()


def create_date():
    # https://pynative.com/python-datetime-format-strftime/
    date = datetime.datetime.now(pytz.timezone('Europe/Zurich'))
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def create_date_from_unix(unix_long):
    date = datetime.datetime.utcfromtimestamp(unix_long / 1000)#.replace(tzinfo=pytz.timezone('Europe/Zurich'))
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def create_id():
    return uuid.uuid4()


if __name__ == "__main__":
    #index = "prices"
    #doc = {"price": 305.86, "venue": "BNB", "@timestamp": create_date()}
    #insert(index, create_id(), doc)
    print(create_date_from_unix(1667661787288))
                                        #1220287113082844499 // 1000000000
