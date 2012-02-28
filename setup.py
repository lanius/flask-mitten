# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

description = """Adds security functions to Flask applications \
for preventing some of the basic threats."""

setup(
    name='Flask-Mitten',
    version='0.1',
    url='https://github.com/lanius/flask-mitten',
    license='BSD',
    author='lanius',
    author_email='lanius@nirvake.org',
    description=description,
    long_description=long_description,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'flask-csrf',
        'Flask-KVSession',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
