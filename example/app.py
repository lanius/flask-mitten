# -*- coding: utf-8 -*-

from flask import Flask, request, session, render_template, url_for, redirect

app = Flask(__name__)
app.debug = False
app.secret_key = 'dummy secret key'

from flaskext.mitten import Mitten, csrf_exempt
mitten = Mitten(app)  # apply Mitten


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/home/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('home.html')


# A POST request is protected from csrf automatically
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        session.regenerate()  # avoid session fixation
        session['username'] = username
        session['logged_in'] = True
        return redirect(url_for('home'))


@app.route('/logout/')
def logout():
    session.destroy()
    return redirect(url_for('home'))


@csrf_exempt  # excluded from csrf protection
@app.route('/public_api/', methods=['POST'])
def public_api():
    return "POST was received successfully.", 200


@app.errorhandler(400)
def exception_handler(error):
    return render_template('error.html')


if __name__ == '__main__':
    app.run(host='localhost', port=8080)
