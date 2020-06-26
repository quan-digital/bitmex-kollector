#!/usr/bin/env python

# python3 setup.py sdist bdist_wheel

from setuptools import setup, find_packages
from os.path import join, dirname

here = dirname(__file__)

setup(name='bitmex_kollector',
      version='0.1.4',
      description="The ultimate data aggregator using Bitmex' Websocket API.",
      long_description=open(join(here, 'README.md')).read(),
      author='canokaue',
      author_email='kaue.cano@quan.digital',
      url='quan.digital',
      install_requires=[
        'websocket-client==0.57.0',
        'requests==2.23.0',
        'pymongo==3.10.1',
        'dnspython==1.16.0',
        'schedule==0.6.0'
      ],
      packages=find_packages(),
      )
