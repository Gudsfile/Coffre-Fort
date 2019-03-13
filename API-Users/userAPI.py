import json, bson, pymongo

from bson import ObjectId
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask_pymongo import PyMongo
from flask_pymongo import MongoClient
from jsonschema import validate

app = Flask(__name__)
'''
app.config['MONGO_DBNAME'] = 'users'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'
'''

try:
	conn = MongoClient()
	print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")

# database
db = conn.users
# Created or Switched to collection names: my_gfg_collection
collection = db.user_collection

"""
API User
"""

app = Flask(__name__)

@app.route('/api')
def index():
    return ("Hello")

@app.route('/api/users', methods=['GET'])
def get_all_users():
    cursor = collection.find()
    output = []
    for u in cursor:
        output.append({'_ID' :str(u['_ID']), 'Login' : u['LOGIN'], 'Password' : u['PASSWORD']})
    return jsonify({'Result' : output})

@app.route('/api/user/id', methods=['GET'])
def get_one_user_id(id = None):
    if id is None:
        id = request.args.get('_ID')
    if bson.objectid.ObjectId.is_valid(id):
        u = collection.find_one({"_ID": ObjectId(id)})
        if u is None:
            return Response(status=404)
        else:
            output = ({'_Id' :str(u['_ID']), 'Login' : u['LOGIN'], 'Password' : u['PASSWORD']})
            return jsonify({'Result' : output})
    else:
        return Response(status=404)

@app.route('/api/user/login', methods=['GET'])
def get_one_user_login(login = None):
    if login is None:
        login = request.args.get('LOGIN')
    u = collection.find_one({"LOGIN": login})
    if u is None:
        return Response(status=404)
    else:
        output = ({'_Id' :str(u['_ID']), 'Login' : u['LOGIN'], 'Password' : u['PASSWORD']})
        return jsonify({'Result' : output})

@app.route('/api/create', methods = ['POST'])
def add_user():
    if (request.is_json):
        content = request.get_json()
        with open("./userSchem.json", "r") as fichier:
            dict_valid = json.load(fichier)
        if (validate_json(content, dict_valid)):
            if get_one_user_login(content['LOGIN']).status_code == 200:
                return Response(status=409)
            else:
                id = ObjectId()
                login = content['LOGIN']
                password = content['PASSWORD']
                new_user = {
                    '_ID':id,
                    'LOGIN':login,
                    'PASSWORD':password
                }
                collection.insert_one(new_user)
                return Response(status=200)
        else:
            print("Invalid json")
            return Response(status=400)
    else:
        print("Request is not json")
        return Response(status=400)

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
    client = MongoClient('mongodb://localhost:27017/')
    db = client['test-database']
    print(app.url_map)
    app.run()
