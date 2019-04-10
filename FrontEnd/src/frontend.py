#!/usr/bin/env python

###############################################################################################################

import sys

import requests
from flask import Flask, render_template, request, session, json, redirect, url_for, jsonify


###############################################################################################################

# Debug
DEBUG = False

# App
app = Flask(__name__, static_url_path='/static')


###############################################################################################################

def main(usr='*', arp='*'):
    global url, url_usr, url_arp
    url_arp = "{}:5001".format(arp)
    url_usr = "{}:5002".format(usr)

    app.secret_key = 'super secret key' # TODO CHANGE
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, host='0.0.0.0', port='5003')


###############################################################################################################


# GET LOGIN - get the login page
@app.route('/')
def access():
    global url_arp
    if session.get('PASSWORD'):
        if session.get('LOGIN'):
            try:
                u = 'http://' + url_arp + '/api'
                headers = {'Authorization': session['PASSWORD']}
                params = {'LOGIN': session['LOGIN']}
                r = requests.get(u, headers=headers, params=params)
                j = json.loads(r.content)
                if j['Authorization'] == 'OK':
                    return render_template('secret.html', ressource=j['Ressource'])
            except Exception as e:
                if DEBUG:
                    print(str(e))
                return render_template('login.html')
    return render_template('login.html')


# POST LOGIN - Sign-in and Sign-up request
@app.route('/', methods=['POST'])
def sign():
    global url_usr
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        type = request.form['type']

        if type == "signup":
            u = 'http://' + url_usr + '/api/create'
            headers = {'Content-Type': 'application/json'}
            data = {'LOGIN': login, 'PASSWORD': password}

            try:
                r = requests.post(u, headers=headers, data=json.dumps(data))

                if r.status_code == 200:
                    error = 'Successful signup.'
                else:
                    error = 'Invalid information. Please try again.'
            except requests.exceptions.ConnectionError as e:
                if DEBUG:
                    print(str(e))
                error = 'Inaccessible service.'
            except requests.exceptions.InvalidURL as e:
                if DEBUG:
                    print(str(e))
                error = 'Inaccessible service.'
            except Exception as e:
                if DEBUG:
                    print(str(e))
                error = 'Inaccessible service.'
            return render_template('login.html', error=error)

        elif type == "signin":
            u = 'http://' + url_usr + '/api/user/signin'
            headers = {'Content-Type': 'application/json'}
            params = {'LOGIN': login, 'PASSWORD': password}
            
            try:
                r = requests.get(u, headers=headers, params=params)

                if r.status_code == 200:
                    print(r.json())
                    res = json.loads(r.json())
                    session['LOGIN'] = res['LOGIN']
                    session['PASSWORD'] = res['PASSWORD']
                    return redirect(url_for('access'))
                elif r.status_code == 408:
                    error = 'Service unavailable'
                else:
                    error = 'Invalid Credentials. Please try again.'
            except requests.exceptions.ConnectionError as e:
                if DEBUG:
                    print(str(e))
                error = 'Inaccessible service.'
            except requests.exceptions.InvalidURL as e:
                if DEBUG:
                    print(str(e))
                error = 'Inaccessible service.'
            except Exception as e:
                if DEBUG:
                    print(str(e))
                error = 'Inaccessible service.'
            return render_template('login.html', error=error)


# GET LOGOUT - logout
@app.route('/logout')
def logout():
    if session.get('LOGIN'):
        session.pop('LOGIN', None)
    if session.get('PASSWORD'):
        session.pop('PASSWORD', None)
    return redirect(url_for('access'))


# GET SECRET - get the secret page
@app.route('/secret')
def secret():
    global url_arp
    if session.get('PASSWORD'):
        if session.get('LOGIN'):
            try:
                u = 'http://' + url_arp + '/api'
                headers = {'Authorization': session['PASSWORD']}
                params = {'LOGIN': session['LOGIN']}
                r = requests.get(u, headers=headers, params=params)
                j = json.loads(r.content)
                if j['Authorization'] == 'OK':
                    return render_template('secret.html')
            except Exception as e:
                if DEBUG:
                    print(str(e))
                return redirect(url_for('access'))
    return redirect(url_for('access'))


###############################################################################################################

if __name__ == '__main__':
    print("frontend.py invoked")
    # pass ip argument
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
