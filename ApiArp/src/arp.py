#!/usr/bin/env python

import sys

import zmq
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)


def main(ip='*'):
    global url
    url = "tcp://{}:9001".format(ip)
    app.run(debug=True, host='0.0.0.0', port=5001)


@app.route('/')
def racine():
    return jsonify({'api': '/api', 'documentation': '/apidocs'})


@app.route('/api', methods=['GET'])
def my_microservice():
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
        description: Le token envoyé est valide
      409:
      	description: Le token envoyé n'est pas valide
    """
    global url

    # msg
    try:
        msg = "{\"LOGIN\":\"" + request.args.get('LOGIN') + "\",\"PASSWORD\":\"" + request.headers.get(
            'Authorization') + "\"}"
    except Exception as err:
        return jsonify({'Authorization': 'KO', 'Error': str(err)})

    # zmq
    context = zmq.Context.instance()
    socket = context.socket(zmq.PAIR)
    socket.bind(url)
    socket.RCVTIMEO = 1000

    socket.send_string(msg)
    msg = socket.recv_string()
    try:
        if str(msg) == 'true':
            response = jsonify({'Authorization': "OK"})
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


if __name__ == '__main__':
    print("arp_sample.py invoked")
    # pass ip argument
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()
