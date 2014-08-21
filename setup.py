#!/usr/bin/python3

from setuptools import setup
setup(name='ocsharetools',
version='1.0',
description='Easy tool to access ownCloud shares',
author='Azelphur',
author_email='support@azelphur.com',
url='https://github.com/Azelphur/owncloud-share-tools',
py_modules=['ocsharetools', 'ocsharetools_gui', 'ocsharetools_cli'],
entry_points = {'gui_scripts': ['ocsharetools = ocsharetools_cli:run']},
install_requires=['requests'])
