# -*- coding: utf-8 -*-
"""
    flaskext.mitten
    ~~~~~~~~~~~~~~~

    Adds security functions to Flask apps for preventing some basic threats.

    :copyright: (c) 2012 by lanius.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

from flask import _request_ctx_stack
from flaskext.kvsession import KVSessionExtension
from flaskext.csrf import csrf, csrf_exempt
from simplekv.memory import DictStore


class Mitten(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.banner = 'Welcome!'
        self.cookie_httponly = True

        app.after_request(self.after_request)

        # Set other extentions to app
        store = DictStore()
        KVSessionExtension(store, app)

        csrf(app)

    def after_request(self, response):
        response.headers['Server'] = self.banner
        response.headers['X-Frame-Options'] = 'DENY'
        if self.cookie_httponly and 'Set-Cookie' in response.headers:
            response.headers['Set-Cookie'] += '; HttpOnly'
        return response
