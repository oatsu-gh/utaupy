#!python
# coding: utf-8
# Copyright (c) oatsu
"""
PyPiからインストールするときに使うやつ
"""

from setuptools import setup

version = '1.6.0'

with open("README.md") as f:
    long_description = f.read()

setup(
    name='utaupy',
    version=version,
    description='Python3 module for UTAU and singing-voice-database',
    author='oatsu',
    author_email='panchi.psp@gmail.com',
    url='https://github.com/oatsu-gh/utaupy/projects',
    install_requires=['pprint'],
    classifiiers=[
        'Programming Language :: Python :: 3'
    ]
)
