#!/usr/bin/env python

from setuptools import setup

setup(name='propertime',
      version='0.2.1',
      description='An attempt at proper time management in Python.',
      long_description="""
Propertime is an attempt to implement proper time management in Python,
by fully embracing the additional complications due to how we measure time
 as humans instead of just denying them.

In a nutshell, it provides two main classes: the ``Time`` class for representing
time (similar to a datetime) and the ``TimeUnit`` class for representing units
of time (similar to timedelta). Such classes play nice with Python datetimes so
that you can mix and match and use them only when needed.

You can have a look at the [README](https://github.com/sarusso/Propertime/blob/main/README.md)
for a better introduction together with some usage examples, and you can get started by having
a look at the [quickstart notebook](https://github.com/sarusso/Propertime/blob/main/Quickstart.ipynb)
or by reading the [reference documentation](https://propertime.readthedocs.io).
      """,
      long_description_content_type='text/markdown',
      url="https://github.com/sarusso/Propertime",
      author='Stefano Alberto Russo',
      author_email='stefano.russo@gmail.com',
      packages=['propertime','propertime.tests'],
      package_data={},
      install_requires = ['python-dateutil >=2.8.2, <3.0.0', 'pytz'],
      license='Apache License 2.0',
      license_files = ('LICENSE',),
    )
