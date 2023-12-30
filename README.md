# Propertime

An attempt at proper time management in Python.

[![Tests status](https://github.com/sarusso/Propertime/actions/workflows/ci.yml/badge.svg)](https://github.com/sarusso/Propertime/actions) [![Licence Apache 2](https://img.shields.io/github/license/sarusso/Propertime)](https://github.com/sarusso/Propertime/blob/main/LICENSE) [![Semver 2.0.0](https://img.shields.io/badge/semver-v2.0.0-blue)](https://semver.org/spec/v2.0.0.html) 


## Quickstart

In a nutshell, Propertime  provides two main classes: ``Time`` for representing time (similar to a datetime) and ``TimeUnit`` for representing units of time (similar to timedelta). 

Such classes are implement assuming two strict and opinionated base hypotheses:

- Time is a floating point number representing the number of seconds passed after the zero on the time axis, which is set to 1st January 1970 UTC, any other representations (as date/hours, time zones, daylight saving times) are built on top of it, and:

- Time units can be of both fixed and *variable* length, if defined with calendar time units as days, weeks, months and years. This means that the length (i.e. the duration in seconds) of a one-day time unit is not defined *unless* it it put in context, which means to know on which time it is applied.

These two assumptions allows Propertime to solve by design many issues in manipulating time that are still present in Python's built-in datetime module as well as in most third-party libraries.

Propertime provides a simple and neat API, and its objects play nice with Python datetimes so that you can mix and match and use it only when needed.

Implementing "proper" time comes indeed at a price: it optimizes for consistency over performance and it is quite strict, meaning that its suitability heavily depends on the use-case.

You can get started by having a look at the [quickstart notebook](Quickstart.ipynb), or by reading the [reference documentation](https://propertime.readthedocs.io).



## Installing

To install Propertime, simply run ``pip install propertime``.

It has just a few requirements, listed in the ``requirements.txt`` file, which you can use to manually install or to setup a virtualenv.


## Testing

Propertime is relatively well tested using the Python unittest module. Just run a ``python -m unittest discover`` in the project root.

To test against different Python versions, you can use Docker. Using Python official images and runtime requirements installation:

    docker run -it -v $PWD:/Propertime python:3.9 /bin/bash -c "cd /Propertime && pip install -r requirements.txt && python -m unittest discover"
    
There is also a ``regression_test.sh`` script that tests, using Docker, from Python 3.6 to Python 3.12.
 


## License
Propertime is licensed under the Apache License version 2.0, unless otherwise specified. See [LICENSE](https://github.com/sarusso/Propertime/blob/master/LICENSE) for the full license text.



