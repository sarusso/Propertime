# Propertime

An attempt at proper time management in Python.

[![Tests status](https://github.com/sarusso/Propertime/actions/workflows/ci.yml/badge.svg)](https://github.com/sarusso/Propertime/actions) [![Licence Apache 2](https://img.shields.io/github/license/sarusso/Propertime)](https://github.com/sarusso/Propertime/blob/main/LICENSE) [![Semver 2.0.0](https://img.shields.io/badge/semver-v2.0.0-blue)](https://semver.org/spec/v2.0.0.html) 


## Quickstart



Propertime is an attempt at implementing proper time management in Python, by fully embracing the intrinsic complications in how we measure an manage time as humans instead of just negating them.

These include but are not limited to: differences between physical and calendar time, time zones, offsets, daylight saving times, undefined calendar time operations and variable length time units.

In a nutshell, Propertime provides two main classes: the ``Time`` class for representing time (similar to a datetime) and the ``TimeUnit`` class for representing units of time (similar to timedelta). 

Such classes are implemented assuming two strict base hypotheses:

- Time is a floating point number corresponding the number of seconds after the zero on the time axis, which is set to 1st January 1970 UTC. Any other representation (as dates and hours, time zones, daylight saving times) are built on top of it.

- Time units can be both of fixed length (for physical time as seconds, minutes, hours) and of *variable* length (for calendar time as days, weeks, months, years). This means that the length (i.e. the duration in seconds) of a calendar time unit is not defined *unless* it is put in a specific context, or in other words to know when it is applied.

These two assumptions allow Propertime to solve by design many issues in manipulating time that are still present in Python's built-in datetime module as well as in most third-party libraries.

Implementing "proper" time comes however at a price: it optimizes for consistency over performance and it is quite strict. Whether it is a suitable solution for you or not, it heavily depends on the use case.

Propertime provides a simple and neat API, it is realitvely well tested and its objects play nice with Python datetimes so that you can mix and match and use it only when needed.

You can get started by reading the [quickstart notebook](Quickstart.ipynb) or by having a look at the [reference documentation](https://propertime.readthedocs.io).



## Installing

To install Propertime, simply run ``pip install propertime``.

It has just a few requirements, listed in the ``requirements.txt`` file, which you can use to manually install or to setup a virtualenv.


## Testing

Propertime is relatively well tested using the Python unittest module.

To run the tests, use the command ``python -m unittest discover`` in the project root.

To test against different Python versions, you can use Docker. Using Python official images and runtime requirements installation:

    docker run -it -v $PWD:/Propertime python:3.9 /bin/bash -c "cd /Propertime && \
    pip install -r requirements.txt && python -m unittest discover"
    
There is also a ``regression_test.sh`` script that tests, using Docker, from Python 3.6 to 3.12.
 


## License
Propertime is licensed under the Apache License version 2.0. See [LICENSE](https://github.com/sarusso/Propertime/blob/master/LICENSE) for the full license text.



