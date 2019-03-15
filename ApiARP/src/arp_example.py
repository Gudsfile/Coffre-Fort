import zmq
from flask import Flask, jsonify
from flask import request

app = Flask(__name__)


@app.route('/api')
def my_microservice():
    """Get token
    ---
    responses:
      200:
        description: Token envoyé est OK
      404:
      	description: Token envoyé pas bon
    """

    # msg
    username ="toto"
    msg = "{\"LOGIN\":\""+username+"\",\"PASSWORD\":\"" + request.headers.get('Authorization') + "\"}"

    # zmq
    context = zmq.Context.instance()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://127.0.0.1:9001")

    while True:
        socket.send_string(msg)
        msg = socket.recv_string()
        print(msg)
        if str(msg) == 'true':
            return jsonify({'Authorization': "OK"})
        else:
            return jsonify({'Authoriation': 'KO'})


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
