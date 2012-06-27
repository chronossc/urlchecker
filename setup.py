#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name="django-urlchecker",
    version="0.0.1",
    description="urlchecker give you a server and a client to collect urls status and use it in your system",
    author="Felipe 'chronos' Prenholato",
    author_email="philipe.rp@gmail.com",
    url="http://github.com/chronossc/urlchecker",
    packages = find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        "Django >= 1.4.0",
        "pylibmc",
        "MySQL-python",
        "raven",
        "south",
        "requests",
        "django-celery"
    ],
    zip_safe = False,
)

