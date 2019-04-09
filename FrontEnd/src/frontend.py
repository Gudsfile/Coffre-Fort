#!/usr/bin/env python

import sys

import requests
from flask import Flask, render_template, request, session, json, redirect, url_for

app = Flask(__name__)


def main(usr='*', arp='*'):
    global url, url_usr, url_arp
    url_arp = "{}:5001".format(arp)
    url_usr = "{}:5002".format(usr)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, host='0.0.0.0', port='5003')


@app.route('/')
def racine():
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
                    return render_template('index.html')
            except Exception as err:
                return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
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
                    return redirect(url_for('racine'))
            except Exception as err:
                return render_template('login.html')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
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
            r = requests.post(u, headers=headers, data=json.dumps(data))

            if r.status_code == 200:
                error = 'Successful, Now connect you.'
                return render_template('login.html', error=error)
            else:
                error = 'Invalid information. Please try again.'
                return render_template('login.html', error=error)

        elif type == "signin":
            u = 'http://' + url_usr + '/api/user/signin'
            headers = {'Content-Type': 'application/json'}
            params = {'LOGIN': login, 'PASSWORD': password}
            r = requests.get(u, headers=headers, params=params)
            if r.status_code == 200:
                print(r.json())
                res = json.loads(r.json())
                session['LOGIN'] = res['LOGIN']
                session['PASSWORD'] = res['PASSWORD']
                return redirect(url_for('login'))
            else:
                error = 'Invalid Credentials. Please try again.'
                return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    if session.get('LOGIN'):
        session.pop('LOGIN', None)
    if session.get('PASSWORD'):
        session.pop('PASSWORD', None)
    return redirect(url_for('login'))


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
            except Exception as err:
                return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/hello')
def hello():
    return render_template('hello.html')


@app.route('/safe')
def safe():
    return render_template('safe.html')


@app.route('/game')
def game():
    return render_template('../static/tower-blocks/index.html')


if __name__ == '__main__':
    print("frontend.py invoked")
    # pass ip argument
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
