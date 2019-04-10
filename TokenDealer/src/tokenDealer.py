###############################################################################################################

import asyncio
import os
import sys
import time

import zmq.asyncio

from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop

import jwt

import json
from jsonschema import validate

###############################################################################################################

# Debug
DEBUG = False

# Key - get the key in the key.txt file, generates a new key if the file was modified a month ago
key = ''
if time.time() - os.path.getmtime('key.txt') >= 2500000:
    os.system('openssl genrsa 1024 > key.txt')
with open('key.txt', 'r') as f:
    data = f.read().splitlines(True)
data = data[1:-1]
for d in data:
    key += d[:-1]
if DEBUG:
    print(key)

# Get the JsonScheme
with open("./userSchem.json", "r") as f:
    jsonValid = json.load(f)


###############################################################################################################

def main(ip_arp="*", ip_usr="*"):
    # Url zmq
    global urlArpTck, urlUsrTck, ctx, queue
    urlArpTck = "tcp://{}:9001".format(ip_arp)
    urlUsrTck = "tcp://{}:9002".format(ip_usr)
    print("Going to bind to: {}".format(urlArpTck))
    print("Going to bind to: {}".format(urlUsrTck))

    # Tell tornado to use asyncio
    AsyncIOMainLoop().install()

    # This must be instantiated after the installing the IOLoop
    queue = asyncio.Queue()
    ctx = zmq.asyncio.Context()

    # Start loop
    zmq_tornado_loop()


###############################################################################################################

async def arp_pulling():
    global urlArpTck
    await pulling(arp_process, urlArpTck)


async def usr_pulling():
    global urlUsrTck
    await pulling(usr_process, urlUsrTck)


# async def generate_key():
#     if time.time() - os.path.getmtime('key.txt') >= 2500000:
#         os.system('openssl genrsa 1024 > key.txt')
#         with open('key.txt', 'r') as f:
#             data = f.read().splitlines(True)
#         data = data[1:-1]
#         for d in data:
#             key += d[:-1]
#         if DEBUG:
#             print(key)
#     time.sleep(2500000)


def zmq_tornado_loop():
    loop = IOLoop.current()
    loop.spawn_callback(arp_pulling)
    loop.spawn_callback(usr_pulling)
    # loop.spawn_callback(generate_key)
    loop.start()


###############################################################################################################

async def pulling(process, url):
    global ctx
    client = ctx.socket(zmq.PAIR)
    client.bind(url)
    while True:
        greeting = await client.recv()
        if DEBUG:
            print(str(greeting))
        client.send_string(process(greeting))


###############################################################################################################

def arp_process(msg):
    # arp_pushing(arp_parse(msg))
    return arp_parse(msg)


def arp_parse(msg):
    res = 'false'
    try:
        j = json.loads(msg)
        if validate_json(j, jsonValid):
            print("\t token receive : \t" + j['PASSWORD'])
            jj = check_token(j['PASSWORD'])
            print("\t token decrypt : \t" + str(jj))
            jj = json.dumps(jj)
            jj = json.loads(str(jj))
            if validate_json(jj, jsonValid):
                if jj['LOGIN'] == j['LOGIN']:
                    res = 'true'
    except Exception as e:
        print("ERROR in : arp_parse()")
        if DEBUG:
            print(str(e))
    return res


###############################################################################################################

def usr_process(msg):
    # usr_pushing(usr_parse(msg))
    return usr_parse(msg)


def usr_parse(msg):
    res = "{\"error\": \"not valid json\"}"
    try:
        j = json.loads(msg)
        if validate_json(j, jsonValid):
            res = "{\"LOGIN\": \"" + j['LOGIN'] + "\", \"PASSWORD\": \"" + str(get_token(j))[2:-1] + "\"}"
    except Exception as e:
        print("ERROR in : usr_parse()")
        if DEBUG:
            print(str(e))
    print(res)
    return res


###############################################################################################################

def get_token(content):
    res = ""
    try:
        res = jwt.encode(content, key, algorithm='HS256')
    except Exception as e:
        print("ERROR in : get_token()")
        if DEBUG:
            print(str(e))
    return res


def check_token(token):
    res = ""
    try:
        res = jwt.decode(token, key, algorithms=['HS256'])
    except Exception as e:
        print("ERROR in : check_token()")
        if DEBUG:
            print(str(e))
    return res


def validate_json(dict_to_test, dict_valid):
    res = False
    try:
        validate(dict_to_test, dict_valid)
    except Exception as e:
        print("ERROR in : validate_json()")
        if DEBUG:
            print("\t validation KO: {}".format(e))
            print(str(e))
    else:
        print("\t validation OK")
        res = True
    return res


###############################################################################################################

if __name__ == "__main__":
    print("tokenDealer.py invoked")
    # pass ip argument
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
