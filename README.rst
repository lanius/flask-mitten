What is Flask-Mitten?
======================

Adds security functions to Flask applications for preventing some of the basic threats.

Features
========

Flask-Mitten supports Flask applications to prevent following threats.

- Clickjacking
- CSRF
- Information disclosure through banner grabbing
- Session fixation

It bundles functions of following Flask extensions.

- `Flask-KVSession <http://flask-kvsession.readthedocs.org/>`_
- `flask-csrf <http://sjl.bitbucket.org/flask-csrf/>`_

More details, see the implementation.


Usage
=====

Installation
------------

Install the extension with the following commands::

    pip install Flask-Mitten

Configuration
-------------

Apply the extention to your app::

    from flaskext.mitten import Mitten
    app = Flask(__name__)
    mitten = Mitten(app)

Request headers are overridden to prevent clickjacking and information disclosure.

If you want to set your own banner, you can do it::

    mitten.banner = "My Nice Banner!"

Preventing Session Fixation
---------------------------

After login, call a regenerate method of session::

    session.regenerate()

The session ID is regenerated, and it prevents session fixation.

Preventing CSRF
---------------

To embed CSRF token, add following line to your template::

    <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}" />

A  POST request is protected against CSRF automatically.

If you want to exclude a route from CSRF protection, use a csrf_exempt decorator::

    @csrf_exempt
    @app.route('/public_api/', methods=['POST'])
    def public_api():
        return "result", 200

More
----

For more details, see an example app.

