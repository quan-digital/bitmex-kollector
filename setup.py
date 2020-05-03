#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import join, dirname

here = dirname(__file__)

setup(name='bitmex_kollector',
      version='0.1.0',
      description="The ultimate data aggregator using Bitmex' Websocket API.",
      long_description=open(join(here, 'README.md')).read(),
      author='canokaue',
      author_email='kaue.cano@quan.digital',
      url='quan.digital',
      install_requires=[
        'websocket-client==0.57.0',
        'requests==2.23.0'
      ],
      packages=find_packages(),
      )
