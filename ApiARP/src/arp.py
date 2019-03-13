from flask import Flask, jsonify
from flask import request
from flasgger import Swagger
import zmq
import random
import sys
import time

app = Flask(__name__)
swagger = Swagger(app)


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
	print("First")
	port = "5000"
	context = zmq.Context.instance()
	socket = context.socket(zmq.PAIR)
	socket.bind("tcp://127.0.0.1:5001")
	while True :
		socket.send_string("Bearer "+request.headers.get('Authorization'))
		msg = socket.recv()
		print (msg)
		if (msg.equals("true")):
			return jsonify({'Authorization': "OK"})
		else :
			return False


if __name__ == '__main__':
	#app.run(debug=True,host='0.0.0.0')
	app.run(host="127.0.0.1",port=5000)
