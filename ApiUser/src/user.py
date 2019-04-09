#!/usr/bin/env python

import bson
import json
import sys
import zmq

from bson import ObjectId
from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
from flask_pymongo import MongoClient
from jsonschema import validate
from flasgger import Swagger
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
swagger = Swagger(app)


def main(ip='*', ip_db='*'):
    global url, collection
    url = "tcp://{}:9002".format(ip)

    app.config['MONGO_DBNAME'] = 'users'
    app.config['MONGO_URI'] = 'mongodb://' + ip_db + ':27017/users'
    '''
    try:
        # Connection
        conn = MongoClient(connect=False)
        print("Connected successfully!!!", flush=True)
        # Database
        db = conn.users
        # Created or Switched to collection names: my_gfg_collection
        collection = db.user_collection
    except:
        print("Could not connect to MongoDB", flush=True)
    '''
    dbconnect = False
    while not dbconnect:
        conn = MongoClient('mongodb://' + ip_db + ':27017/', serverSelectionTimeoutMS=5000, connectTimeoutMS=200000)
        try:
            conn.server_info()  # force connection on a request as the
            # connect=True parameter of MongoClient seems
            # to be useless here
            # Database
            db = conn.users
            # Created or Switched to collection names: my_gfg_collection
            collection = db.user_collection
            dbconnect = True
        except ServerSelectionTimeoutError as err:
            # do whatever you need
            print(err)
            print("Could not connect to MongoDB", flush=True)

    # client = MongoClient('mongodb://' + ip_db + ':27017/')
    # db = client['test-database']
    # print(app.url_map, flush=True)
    app.run(debug=True, host='0.0.0.0', port='5002')


@app.route('/')
def index():
    return jsonify({'documentation': '/apidocs', 'get_all_users': '/api/users', 'get_one_user_id': '/api/user/id',
                    'get_one_user_login': '/api/user/login', 'get_one_user_signin': '/api/user/signin',
                    'add_user': '/api/create'})


@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all users in db
    ---
    responses:
      200:
        description: Liste des utilisation en db
        type: application/json
    """
    global collection
    cursor = collection.find()
    output = []
    for u in cursor:
        output.append({'_ID': str(u['_ID']), 'Login': u['LOGIN']})
    return jsonify({'Result': output})


@app.route('/api/user/id', methods=['GET'])
def get_one_user_id(id=None):
    """Get one user in db with the id
    ---
    parameters:
      - name: _ID
        in: query
        type: int
        required: true
        default: None
    responses:
      200:
        description: Utilisateur trouvé
        type: application/json
      404:
      	description: Utilisateur non trouvé
    """
    global collection
    if id is None:
        id = request.args.get('_ID')
    if bson.objectid.ObjectId.is_valid(id):
        u = collection.find_one({"_ID": ObjectId(id)})
        if u is None:
            return Response(status=404)
        else:
            output = ({'_Id': str(u['_ID']), 'Login': u['LOGIN']})
            response = jsonify({'Result': output})
            response.status_code = 200
            return response
    else:
        return Response(status=404)


@app.route('/api/user/login', methods=['GET'])
def get_one_user_login(login=None):
    """Get one user in db with the login
    ---
    parameters:
      - name: LOGIN
        in: query
        type: string
        required: true
        default: None
    responses:
      200:
        description: Utilisateur trouvé
        type: application/json
      404:
      	description: Utilisateur non trouvé
    """
    global collection
    if login is None:
        login = request.args.get('LOGIN')
    u = collection.find_one({"LOGIN": login})
    if u is None:
        return Response(status=404)
    else:
        output = ({'_Id': str(u['_ID']), 'Login': u['LOGIN']})
        response = jsonify({'Result': output})
        response.status_code = 200
        return response


@app.route('/api/user/signin', methods=['GET'])
def get_one_user_signin(login=None, password=None):
    """Get one user in db with the login and the password
    ---
    parameters:
      - name: LOGIN
        in: query
        type: string
        required: true
        default: None
      - name: PASSWORD
        in: query
        type: string
        required: true
        default: None
    responses:
      200:
        description: Utilisateur trouvé
        type: application/json
      404:
        description: Utilisateur non trouvé
        type: application/json
    """
    global collection
    if login is None:
        login = request.args.get('LOGIN')
    if password is None:
        password = request.args.get('PASSWORD')
    u = collection.find_one({"LOGIN": login, "PASSWORD": password})
    if u is None:
        return Response(status=404)
    else:
        global url
        # zmq
        context = zmq.Context.instance()
        socket = context.socket(zmq.PAIR)
        socket.bind(url)
        socket.RCVTIMEO = 1000

        socket.send_string("{\"LOGIN\":\"" + login + "\",\"PASSWORD\":\"" + password + "\"}")
        msg = socket.recv_string()
        try:
            response = jsonify(msg)
            response.status_code = 200
        except Exception as err:
            response = jsonify({'Error': str(err)})
            response.status_code = 404
        return response


@app.route('/api/create', methods=['POST'])
def add_user():
    """Add one user
    ---
    parameters:
      - in: body
        type: application/json
        required: true
        default: None
    responses:
      200:
        description: Utilisateur ajouté
      400:
        description: Utilisateur non ajouté
    """
    global collection
    if request.is_json:
        content = request.get_json()
        with open("./userSchem.json", "r") as file:
            dict_valid = json.load(file)
        if validate_json(content, dict_valid):
            if get_one_user_login(content['LOGIN']).status_code == 200:
                return Response(status=400)
            else:
                id = ObjectId()
                login = content['LOGIN']
                password = content['PASSWORD']
                new_user = {
                    '_ID': id,
                    'LOGIN': login,
                    'PASSWORD': password
                }
                collection.insert_one(new_user)
                return Response(status=200)
        else:
            print("Invalid json")
            return Response(status=400)
    else:
        print("Request is not json")
        return Response(status=400)


# Check the json
def validate_json(dict_to_test, dict_valid):
    try:
        validate(dict_to_test, dict_valid)
    except Exception as valid_err:
        print("Validation KO: {}".format(valid_err))
        return False
    else:
        print("Validation OK")
        return True


if __name__ == '__main__':
    print("user.py invoked")
    # pass ip argument
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
