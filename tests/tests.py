# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cookielib
import unittest
import re
from itertools import chain

from werkzeug.exceptions import BadRequest, Forbidden

import example.app


class MittenTestCase(unittest.TestCase):

    def setUp(self):
        self.app = example.app.app.test_client()
        self.mitten = example.app.mitten

    def test_banner(self):
        rv = self.app.get('/')
        assert 'Welcome' in rv.headers['Server']

    def test_custom_banner(self):
        custom_banner = 'Custom Banner'
        self.mitten.banner = custom_banner
        rv = self.app.get('/')
        assert rv.headers['Server'] == custom_banner

    def test_clickjacking(self):
        rv = self.app.get('/')
        assert rv.headers['X-Frame-Options'] == 'DENY'

    def test_httponly(self):
        rv = self.app.get('/login/')
        assert 'HttpOnly' in rv.headers['Set-Cookie']

    def test_httponly_false(self):
        self.mitten.cookie_httponly = False
        rv = self.app.get('/login/')
        assert 'HttpOnly' not in rv.headers['Set-Cookie']

    def test_session_fixation(self):
        rv_before = self.app.get('/login/')
        cookie_before = self.parse_cookie(rv_before.headers['Set-Cookie'])
        csrf_token = self.get_csrf_token(rv_before.data)

        rv_after = self.app.post('/login/', data={
            'username': 'myname',
            'password': 'mypass',
            '_csrf_token': csrf_token
        }, follow_redirects=True)
        cookie_after = self.parse_cookie(rv_after.headers['Set-Cookie'])
        assert 'Welcome' in rv_after.data  # login was success
        assert cookie_before['session'] != cookie_after['session']

    def test_csrf(self):
        def post():
            self.app.post('/login/', data={
                'username': 'myname',
                'password': 'mypass'
            }, follow_redirects=True)
        self.assertRaises(BadRequest, post)

    def test_csrf_exempt(self):
        rv = self.app.post('/public_api/')
        assert 'success' in rv.data

    def test_json_fail(self):
        def get():
            self.app.get('/json_api/')
        self.assertRaises(Forbidden, get)

    def test_json_success(self):
        headers = [('X-Requested-With', 'XMLHttpRequest')]
        rv = self.app.get('/json_api/', headers=headers)
        assert 'success' in rv.data
        assert 'application/json' in rv.headers['Content-Type']
        assert 'charset=utf-8' in rv.headers['Content-Type']
        assert rv.headers['X-Content-Type-Options'] == 'nosniff'

    def test_xss_protection(self):
        rv = self.app.get('/')
        assert rv.headers['X-XSS-Protection'] == '1'

    def parse_cookie(self, cookie_str):
        parsed = cookielib.parse_ns_headers([cookie_str])
        return dict(chain(*parsed))

    def get_csrf_token(self, html):
        pat = r'.*<input.*name="_csrf_token".*value="([a-z0-9\-]*)"'
        return re.match(pat, html.replace('\n', '')).group(1)


if __name__ == '__main__':
    unittest.main()
