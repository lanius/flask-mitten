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
        self.assertTrue('Welcome' in rv.headers['Server'])

    def test_custom_banner(self):
        custom_banner = 'Custom Banner'
        self.mitten.banner = custom_banner
        rv = self.app.get('/')
        self.assertEqual(rv.headers['Server'], custom_banner)

    def test_clickjacking(self):
        rv = self.app.get('/')
        self.assertEqual(rv.headers['X-Frame-Options'], 'DENY')

    def test_httponly(self):
        rv = self.app.get('/login/')
        self.assertTrue('HttpOnly' in rv.headers['Set-Cookie'])

    def test_httponly_false(self):
        self.mitten.cookie_httponly = False
        rv = self.app.get('/login/')
        self.assertTrue('HttpOnly' not in rv.headers['Set-Cookie'])

    def test_session_fixation(self):
        get_login_rv = self.app.get('/login/')
        before_session_id = self.get_session_id(get_login_rv)
        csrf_token = self.get_csrf_token(get_login_rv)

        post_login_rv = self.login(csrf_token)
        after_session_id = self.get_session_id(post_login_rv)
        self.assertTrue('Welcome' in post_login_rv.data)  # login was success
        self.assertNotEqual(before_session_id, after_session_id)

    def test_csrf(self):
        rv = self.login()
        self.assertEqual(rv.status, '400 BAD REQUEST')

    def test_csrf_exempt(self):
        rv = self.app.post('/public_api/')
        self.assertTrue('success' in rv.data)

    def test_json_fail(self):
        rv = self.app.get('/json_api/')
        self.assertEqual(rv.status, '403 FORBIDDEN')

    def test_json_success(self):
        headers = [('X-Requested-With', 'XMLHttpRequest')]
        rv = self.app.get('/json_api/', headers=headers)
        self.assertTrue('success' in rv.data)
        self.assertTrue('application/json' in rv.headers['Content-Type'])
        self.assertTrue('charset=utf-8' in rv.headers['Content-Type'])
        self.assertEqual(rv.headers['X-Content-Type-Options'], 'nosniff')

    def test_xss_protection(self):
        rv = self.app.get('/')
        self.assertEqual(rv.headers['X-XSS-Protection'], '1')

    def get_login_csrf_token(self):
        rv = self.app.get('/login/')
        return self.get_csrf_token(rv)

    def login(self, csrf_token=None):
        data = {'username': 'myname', 'password': 'mypass'}
        if csrf_token:
            data['_csrf_token'] = csrf_token
        return self.app.post('/login/', data=data, follow_redirects=True)

    def get_csrf_token(self, rv):
        pat = r'.*<input.*name="_csrf_token".*value="([a-z0-9\-]*)"'
        return re.match(pat, rv.data.replace('\n', '')).group(1)

    def get_session_id(self, rv):
        cookie = self.parse_cookie(rv.headers['Set-Cookie'])
        return cookie['session']

    def parse_cookie(self, cookie_str):
        parsed = cookielib.parse_ns_headers([cookie_str])
        return dict(chain(*parsed))


if __name__ == '__main__':
    unittest.main()
