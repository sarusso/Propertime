# Propertime

An attempt at proper time management in Python.

[![Tests status](https://github.com/sarusso/Propertime/actions/workflows/ci.yml/badge.svg)](https://github.com/sarusso/Propertime/actions) [![Licence Apache 2](https://img.shields.io/github/license/sarusso/Propertime)](https://github.com/sarusso/Propertime/blob/main/LICENSE) [![Semver 2.0.0](https://img.shields.io/badge/semver-v2.0.0-blue)](https://semver.org/spec/v2.0.0.html) 

## Introduction


Propertime is an attempt at implementing proper time management in Python, by fully embracing the extra complications arising due to the intrinsic need of conflating together physical and calendar time instead of neglecting them.

These include, but are not limited to: time representations, time zones, UTC offsets, daylight saving times, undefined calendar time operations and variable length time spans.

For example, while physical time (seconds, minutes and hours) is always well-defined, calendar time (days, weeks, months and years) is entirely dependent on human conventions and it is often ill-defined: the time of a day without a time zone does not make much sense, a generic day can last either 23, 24 or 25 hours depending on the daylight saving time (DST) switch, and the result of adding a month to the 31st of January is just not defined.

Propertime tries to embrace such complexity and eliminate ambiguity without overcomplicating the code or its interfaces, with the intent of providing a viable solution for common time management issues.

In a nutshell, it provides two main classes: the ``Time`` class for representing time (similar to a datetime) and the ``TimeSpan`` class for representing time spans (similar to a timedelta).

Such classes are implemented assuming two strict hypotheses:

- **Time** is a floating point number corresponding the number of seconds after the zero on the time axis (Epoch), which is set to 1st January 1970 UTC. Any other representations (as dates and hours, time zones, daylight saving times) are built on top of it.

- **Time spans** can be either of fixed length (for physical time as seconds, minutes, hours) and  of *variable* length (for calendar time as days, weeks, months, years). This means that the length (i.e. the duration in seconds) of a time span involving calendar components is not defined *unless* it is put in a specific context, or in other words knowing when it is applied.

These two assumptions allow Propertime to adress by design many issues of time manipulation that are still present in Python's built-in datetime module as well as most third-party libraries.

Propertime provides a simple and neat API, it is relatively well tested and it plays nice with Python datetimes so that you can mix and match and use it only when needed.

Implementing "proper" time comes at a price, though: the library is optimized for consistency over performance and its interfaces are quite strict. Whether it is a suitable solution for you or not, it heavily depends on your use case.

You can get started by having a look at the example usage below, reading the [quickstart notebook](Quickstart.ipynb) or checking out the [API documentation](https://propertime.readthedocs.io).


## Installing

To install Propertime, simply run ``pip install propertime``.

It has just a few requirements, listed in the ``requirements.txt`` file, which you can use to manually install or to setup a virtualenv.


## Example usage

```python
# Time
from propertime import Time, Timespan

time_now = Time() # If no arguments, time is now

time = Time(1703517120.0) # Init from Epoch (UTC)

time = Time(2023,5,6,13,45) # Init datetime-like. Defaults to UTC, there is no
                            # such thing as naive time (without time zone/offset)

time = Time(2023,5,6,13,45, tz='US/Eastern') # Init datetime-like and easily
                                             # set time zone as string

time = Time(2023,11,5,1,15, tz='US/Eastern') # This is ambiguous: there are
                                             # "two" 1:15 AM on DST change

time = Time(2023,3,12,2,30, tz='US/Eastern') # This just does not exist on
                                             # US/Eastern, due to DST change

# Time spans
time + TimeSpan('1D') # Tomorrow same hour. Not defined when DTS starts, and
                      # ambiguous when DTS ends

time + TimeSpan('24h') # Tomorrow same hour unless applied over a DTS change,
                       # where there will be a plus or minus 1 hour difference

time + TimeSpan('1M') # Next month same day. Not defined if the destination day
                      # does not exist (i.e. 30th of February)


# Conversions
time = Time.from_iso('2023-12-25T16:12:00+01:00') # Convert from ISO string,
                                                  # similar for datetimes

time.to_iso() # Convert to ISO string, similar for datetimes
```


## Testing

Propertime is relatively well tested using the Python unittest module.

To run the tests, use the command ``python -m unittest discover`` in the project root.

To test against different Python versions, you can use Docker. Using Python official images and runtime requirements installation:

    docker run -it -v $PWD:/Propertime python:3.9 /bin/bash -c "cd /Propertime && \
    pip install -r requirements.txt && python -m unittest discover"
    
There is also a ``regression_test.sh`` script that tests, using Docker, from Python 3.6 to 3.12.


## License
Propertime is licensed under the Apache License version 2.0. See [LICENSE](https://github.com/sarusso/Propertime/blob/master/LICENSE) for the full license text.



