#!/usr/bin/env python

###############################################################################################################

import sys

import zmq
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger

###############################################################################################################

app = Flask(__name__)
swagger = Swagger(app)


###############################################################################################################


def main(ip='*'):
    global url, ressource
    url = "tcp://{}:9001".format(ip)
    with open('ressource.txt', 'r') as f:
        ressource = f.read()
    app.run(debug=True, host='0.0.0.0', port=5001)


###############################################################################################################

@app.route('/')
def racine():
    return jsonify({'api': '/api', 'documentation': '/apidocs'})


@app.route('/api', methods=['GET'])
def get_token():
    """Get token
    ---
    parameters:
      - name: Authorization
        in: header
        description: token
        required: true
        type: string
      - name: LOGIN
        in: query
        type: string
        required: true
    responses:
      200:
        description: Le token envoyé est valide, la ressource est envoyé
      409:
        description: Le token envoyé n'est pas valide
    """
    global url, ressource

    # msg
    try:
        msg = "{\"LOGIN\":\"" + request.args.get('LOGIN') + "\",\"PASSWORD\":\"" + request.headers.get(
            'Authorization') + "\"}"
    except Exception as err:
        return jsonify({'Authorization': 'KO', 'Error': str(err)})

    # zmq
    context = zmq.Context.instance()
    socket = context.socket(zmq.PAIR)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.AFFINITY, 1)
    socket.setsockopt(zmq.RCVTIMEO, 2000)

    print(url)
    socket.connect(url)

    socket.send_string(msg)
    try:
        msg = socket.recv_string()
        if str(msg) == 'true':
            response = jsonify({'Authorization': "OK", 'Ressource': ressource})
            response.status_code = 200
            return response
        else:
            response = jsonify({'Authorization': "KO"})
            response.status_code = 409
            return response
    except Exception as err:
        response = jsonify({'Authorization': 'KO', 'Error': str(err)})
        response.status_code = 409
        return response
    finally:
        socket.close()  # ____POLICY: graceful termination
        context.term()  # ____POLICY: graceful termination


###############################################################################################################

if __name__ == '__main__':
    print("arp.py invoked")
    # pass ip argument
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
