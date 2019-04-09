###############################################################################################################

import asyncio
import sys

import zmq.asyncio

from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop

import jwt

import json
from jsonschema import validate

###############################################################################################################

# Debug
DEBUG = False

# Key
key = "MIICXAIBAAKBgQC3xqGNIyHq1a5vFaR+anh6n744bwlIQh56yrus/ds/khtsJt+8NHWAYa43Te04Ri9Hdhntyv+p3d1AcBr/OrBWrJzZO00Asz" \
      "/xXRx7uUkTxay4alvTdMBuImEadeWd8AobLM9OfaZCT5rHb1KjPVeuVNzpzA2Eu21xfWCRIeqXeQIDAQABAoGAfJJgH9OYwh5mR1ZcUnTJhhWS" \
      "U56wpBJtpr6VyQWrAMSBYiZXsrO8knGkLkjcbDDnC4G6wb3A39xMhcl4A1o8/N1p0I7/+/0tVDrIf5qd3NG347jdfSZQE9X5f0wT7gOdAHFW+A" \
      "wSvehx6YdW/LQE5RJbNi5tJnbBH179GJUNwoECQQDhw0C4x0MC20bvVfmjAebC3zUYHiqb81nKd6tBaKXi/0kRHCO/QhnDfjRyDQOmPfCM4vqR" \
      "Row4OYdpC1Rb3eGNAkEA0GPF0pjbEmWUZEwkTJmP2ra1Jv2uudZJjjA3KPG7MzJaKZRo0xMZ3mc/K436n2+Hhjv+kmV8EBcodCbQ4mlUnQJBAK" \
      "PneamtIP23pWCM0PDg6nlXGa8EcvYwV7TZejuHW5w="

# Get the JsonScheme
with open("./userSchem.json", "r") as file:
    jsonValid = json.load(file)


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


# Server Pushing
# serverArp = ctx.socket(zmq.PAIR)
# serverArp.bind(urlTckArp)
# serverUsr = ctx.socket(zmq.PAIR)
# serverUsr.bind(urlTckUsr)


###############################################################################################################

async def arp_pulling():
    global urlArpTck
    await pulling(arp_process, urlArpTck)


async def usr_pulling():
    global urlUsrTck
    await pulling(usr_process, urlUsrTck)


def zmq_tornado_loop():
    loop = IOLoop.current()
    loop.spawn_callback(arp_pulling)
    loop.spawn_callback(usr_pulling)
    loop.start()


###############################################################################################################

async def pulling(process, url):
    global ctx
    client = ctx.socket(zmq.PAIR)
    client.connect(url)
    while True:
        greeting = await client.recv()
        print(str(greeting))
        # process(greeting)
        client.send_string(process(greeting))


# def pushing(server, msg):
#     server.send_string(msg)
#     asyncio.sleep(1)


###############################################################################################################

def arp_process(msg):
    # arp_pushing(arp_parse(msg))
    return arp_parse(msg)


# def arp_pushing(msg):
#     pushing(serverArp, msg)


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


# def usr_pushing(msg):
#     pushing(serverUsr, msg)


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
