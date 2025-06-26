#! /usr/bin/env python3
# Copyright (c) 2020-2025 oatsu
"""
Python script for PyPI registation
"""
from setuptools import find_packages, setup

version = '1.21.0'

try:
    with open("README.md", mode='r', encoding='utf-8') as f:
        long_description = f.read()
except UnicodeDecodeError:
    with open("README.md", mode='r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='utaupy',
    version=version,
    description='Python3 module for UTAU and singing-databases',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='oatsu',
    author_email='oatsu.dev@gmail.com',
    maintainer='oatsu',
    maintainer_email='oatsu.dev@gmail.com',
    url='https://github.com/oatsu-gh/utaupy',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    keywords=['UTAU']
)
