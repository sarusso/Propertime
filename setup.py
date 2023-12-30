#!/usr/bin/env python

from setuptools import setup

setup(name='propertime',
      version='0.1.1',
      description='An attempt at proper time management in Python.',
      long_description="""
Propertime is an attempt at proper time management in Python.

In a nutshell, it provides two main classes: ``Time`` for representing time (similar to a datetime) 
and ``TimeUnit`` for representing units of time (similar to timedelta). 

Such classes are implement assuming two strict and opinionated base hypotheses:

- Time is a floating point number representing the number of seconds passed after the zero on the time axis, 
  which is set to 1st January 1970 UTC, any other representations (as date/hours, time zones, daylight saving times) 
  are built on top of it, and:

- Time units can be of both fixed and *variable* length, if defined with calendar time units as days, weeks, months and years.
  This means that the length (i.e. the duration in seconds) of a one-day time unit is not defined *unless* it it put in context, 
  which means to know on which time it is applied.

These two assumptions allows Propertime to solve by design many issues in manipulating time that are still present in Python's
built-in datetime module as well as in most third-party libraries.

Propertime provides a simple and neat API, and its objects play nice with Python datetimes so that you can mix and match and use it
only when needed. Implementing "proper" time comes indeed at a price: it optimizes for consistency over performance and it is quite
strict, meaning that its suitability heavily depends on the use-case.

You can get started by having a look at the [quickstart notebook](https://github.com/sarusso/Propertime/blob/main/Quickstart.ipynb),
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
