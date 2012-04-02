# -*- coding: utf-8 -*-
"""
    flaskext.mitten
    ~~~~~~~~~~~~~~~

    Adds security functions to Flask apps for preventing some basic threats.

    :copyright: (c) 2012 by lanius.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

from flask import _request_ctx_stack, abort, request
from flaskext.kvsession import KVSessionExtension
from flaskext.csrf import csrf, csrf_exempt
from simplekv.memory import DictStore


class Mitten(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.banner = 'Welcome!'
        self.cookie_httponly = True
        self._json_views = []

        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)

        # Set other extentions to app
        store = DictStore()
        KVSessionExtension(store, self.app)

        csrf(self.app)
        self.csrf_exempt = csrf_exempt

    def before_request(self):
        ctx = _request_ctx_stack.top
        dest = self.app.view_functions.get(request.endpoint)
        ctx.request_json = dest in self._json_views
        if ctx.request_json:
            if not request.is_xhr:
                ctx.forbidden = True
                abort(403)
            else:
                ctx.forbidden = False

    def after_request(self, response):
        ctx = _request_ctx_stack.top
        headers = response.headers
        headers['Server'] = self.banner
        headers['X-Frame-Options'] = 'DENY'
        headers['X-XSS-Protection'] = '1'
        if self.cookie_httponly and 'Set-Cookie' in response.headers:
            headers['Set-Cookie'] += '; HttpOnly'
        if ctx.request_json and not ctx.forbidden:
            headers['Content-Type'] = 'application/json; charset=utf-8'
            headers['X-Content-Type-Options'] = 'nosniff'
        return response

    def json(self, view):
        self._json_views.append(view)
        return view
