#!python
# coding: utf-8
# Copyright (c) oatsu
"""
Python script for PyPI registation
"""
from setuptools import setup

version = '1.6.0.0'

try:
    with open("README.md", mode='r') as f:
        long_description = f.read()
except UnicodeDecodeError:
    with open("README.md", mode='r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='utaupy',
    version=version,
    description='Python3 module for UTAU and singing-voice-database',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='oatsu',
    author_email='panchi.psp@gmail.com',
    maintainer='oatsu',
    maintainer_email='panchi.psp@gmail.com',
    url='https://github.com/oatsu-gh/utaupy',
    install_requires=['pprint'],
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    keywords=['UTAU']
)
