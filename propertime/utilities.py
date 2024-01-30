# -*- coding: utf-8 -*-
"""Time manipulation utilities"""

import datetime, calendar, pytz
from dateutil.tz.tz import tzoffset
try:
    from zoneinfo import ZoneInfo
except:
    ZoneInfo = None

import logging
logger = logging.getLogger(__name__)

UTC = pytz.UTC

def timezonize(tz):
    """Convert a string representation of a time zone to its pytz object, or
    do nothing if the argument is already a pytz time zone or tzoffset, or None."""

    # Checking if something is a valid pytz object is hard as it seems that they are spread around the pytz package.
    #
    # Option 1): Try to convert if string or unicode, otherwise try to instantiate a datetieme object decorated
    # with the time zone in order to check if it is a valid one. 
    #
    # Option 2): Get all members of the pytz package and check for type, see
    # http://stackoverflow.com/questions/14570802/python-check-if-object-is-instance-of-any-class-from-a-certain-module
    #
    # Option 3) perform a hand-made test. We go for this one, tests would fail if something changes in this approach.

    if tz is None:
        return tz

    if isinstance(tz,tzoffset):
        return tz

    if ZoneInfo and isinstance(tz, ZoneInfo):
        return tz

    if not 'pytz' in str(type(tz)):
        tz = pytz.timezone(tz)

    return tz


def is_dt_inconsistent(dt):
    """Check that a datetieme object is consistent with its time zone (some conditions can lead to
    have summer time set in winter, or to end up in non-existent times as when changing DST)."""

    # https://en.wikipedia.org/wiki/Tz_database
    # https://www.iana.org/time-zones

    if dt.tzinfo is None:
        return False
    else:

        # This check is quite heavy but there is apparently no other way to do it.
        if dt.utcoffset() != dt_from_s(s_from_dt(dt), tz=dt.tzinfo).utcoffset():
            return True
        else:
            return False


def is_dt_ambiguous_without_offset(dt):
    """Check if a datetime object is specified in an ambiguous way on a given time zone"""

    dt_minus_one_hour_via_UTC = UTC.localize(datetime.datetime.utcfromtimestamp(s_from_dt(dt)-3600)).astimezone(dt.tzinfo)
    if dt.hour == dt_minus_one_hour_via_UTC.hour:
        return True

    dt_plus_one_hour_via_UTC = UTC.localize(datetime.datetime.utcfromtimestamp(s_from_dt(dt)+3600)).astimezone(dt.tzinfo)
    if dt.hour == dt_plus_one_hour_via_UTC.hour:
        return True

    return False


def now_s():
    """Return the current time in epoch seconds."""
    return calendar.timegm(now_dt().utctimetuple())


def now_dt(tz='UTC'):
    """Return the current time in datetime format."""
    if tz != 'UTC':
        raise NotImplementedError()
    return datetime.datetime.utcnow().replace(tzinfo = pytz.utc)


def dt(*args, **kwargs):
    """Initialize a datetime object with the time zone in the proper way. Using the standard
    datetime initialization leads to various problems if setting a pytz time zone.

    Args:
        year(int): the year.
        month(int): the month.
        day(int): the day.
        hour(int): the hour, defaults to 0.
        minute(int): the minute, Defaults to 0.
        second(int): the second, Defaults to 0.
        microsecond(int): the microsecond, Defaults to None.
        naive(bool): if to create a naive (without time zone) datetime.
        tz(tzinfo, pytz, str): the time zone, defaults to UTC or None if naive is set.
        offset_s(int,float): an optional offset, in seconds.
        trustme(bool): if to skip sanity checks. Defaults to False.
        guessing(bool): if to enable guessing mode and guess in ambiguous situations.
    """

    naive = kwargs.pop('naive', False)
    tz = kwargs.pop('tz', None)
    if naive and tz is not None:
        raise ValueError('Set naive=True but also set a time zone ({}): chose which one'.format(tz))
    if not naive and tz is None:
        tz = UTC
    offset_s = kwargs.pop('offset_s', None)
    trustme = kwargs.pop('trustme', False)
    guessing = kwargs.pop('guessing', False)

    if kwargs:
        raise Exception('Unhandled arg: "{}".'.format(kwargs))

    if tz is not None:
        tz = timezonize(tz)

    if offset_s is not None:

        # Special case for the offset in seconds
        time_dt = datetime.datetime(*args, tzinfo=tzoffset(None, offset_s))

        # And get it on the required time zone if any
        if tz:
            time_dt = as_tz(time_dt, tz)

    else:

        # Standard time zone or tzoffset
        if not tz:
            time_dt = datetime.datetime(*args)
        elif isinstance(tz, tzoffset):
            time_dt = datetime.datetime(*args, tzinfo=tz)
        else:
            time_dt = tz.localize(datetime.datetime(*args))

        if not trustme and tz and tz != UTC:
            if is_dt_ambiguous_without_offset(time_dt):
                time_dt_naive = time_dt.replace(tzinfo=None)
                if not guessing:
                    raise ValueError('Sorry, time {} is ambiguous on time zone {} without an offset'.format(time_dt_naive, tz))
                else:
                    # TODO: move to a _get_utc_offset() support function. Used also in Time __str__.
                    iso_time_part = str_from_dt(time_dt).split('T')[1]
                    if '+' in iso_time_part:
                        offset_assumed = '+'+iso_time_part.split('+')[1]
                    else:
                        offset_assumed = '-'+iso_time_part.split('-')[1]
                    logger.warning('Time {} is ambiguous on time zone {}, assuming {} UTC offset'.format(time_dt_naive, tz, offset_assumed))

    # Check consistency
    if not trustme and tz and tz != UTC:
        if is_dt_inconsistent(time_dt):
            time_dt_naive = time_dt.replace(tzinfo=None)
            raise ValueError('Sorry, time {} does not exist on time zone {}'.format(time_dt_naive, tz))

    return time_dt

def get_tz_offset(dt):
    """Get the time zone offset, in seconds."""
    return s_from_dt(dt.replace(tzinfo=UTC)) - s_from_dt(dt)

def get_offset_from_dt(dt):
    """Get the offset from a datetime, in seconds."""
    sign = -1 if dt.utcoffset().days < 0 else 1
    offset = sign * dt.utcoffset().seconds
    return offset

def correct_dt_dst(dt):
    """Correct the DST of a datetime object, by re-creating it."""

    # https://en.wikipedia.org/wiki/Tz_database
    # https://www.iana.org/time-zones

    if dt.tzinfo is None:
        return dt

    # Create and return a New datetime object. This corrects the DST if errors are present.
    return __dt(dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                dt.microsecond,
                tz=dt.tzinfo)


def as_tz(dt, tz):
    """Get a datetime object as if it was on the given time zone.

    Arguments:
        dt(datetime): the datetime object.
        tz(tzinfo,pytz,str): the time zone.
    """
    if dt.tzinfo is None:
        raise ValueError('Cannot get naive datetimes as if on other time zones')
    return dt.astimezone(timezonize(tz))


def dt_from_s(s, tz='UTC'):
    """Create a datetime object from epoch seconds. If no time zone is given, UTC is assumed."""

    try:
        timestamp_dt = datetime.datetime.utcfromtimestamp(float(s))
    except TypeError:
        raise TypeError('The s argument must be string or number, got {}'.format(type(s)))

    pytz_tz = timezonize(tz)
    timestamp_dt = timestamp_dt.replace(tzinfo=pytz.utc).astimezone(pytz_tz)

    return timestamp_dt


def s_from_dt(dt, tz=None):
    """Return the epoch seconds from a datetime object, with floating point for milliseconds/microseconds."""
    if not (isinstance(dt, datetime.datetime)):
        raise TypeError('Function called without datetime argument, got "{}" instead'.format(dt.__class__.__name__))
    try:
        if dt.tzinfo is None and tz is None:
            raise ValueError('Cannot convert to epoch seconds naive datetimes')
        elif tz is not None:
            tz = timezonize(tz)
            dt = tz.localize(dt)
        # This is the only safe approach. Some versions of Python around 3.4.4 - 3.7.3
        # get the datetime.timestamp() wrong and compute seconds on local time zone.
        microseconds_part = (dt.microsecond/1000000.0) if dt.microsecond else 0
        return (calendar.timegm(dt.utctimetuple()) + microseconds_part)

    except TypeError:
        # This catch and tris to circumnavigate a specific bug in Pandas Timestamp():
        # TypeError: an integer is required (https://github.com/pandas-dev/pandas/issues/32174)
        return dt.timestamp()


def dt_from_str(string, tz=None):
    """Create a datetime object from a string.

    This is a basic IS0 8601, see https://www.w3.org/TR/NOTE-datetime

    Supported formats on UTC:
        1) YYYY-MM-DDThh:mm:ssZ
        2) YYYY-MM-DDThh:mm:ss.{u}Z

    Supported formats with offset    
        3) YYYY-MM-DDThh:mm:ss+ZZ:ZZ
        4) YYYY-MM-DDThh:mm:ss.{u}+ZZ:ZZ

    Other supported formats:
        5) YYYY-MM-DDThh:mm:ss (without the trailing Z, treated as naive)
    """

    # Split and parse standard part
    if 'T' in string:
        date, time = string.split('T')
    elif ' ' in string:
        date, time = string.split(' ')
    else:
        raise ValueError('Cannot find any date/time separator (looking for "T" or " " in "{}")'.format(string))

    # UTC
    if time.endswith('Z'):
        tz='UTC'
        offset_s = 0
        time = time[:-1]

    # Positive offset
    elif ('+') in time:
        time, offset = time.split('+')
        offset_s = (int(offset.split(':')[0])*60 + int(offset.split(':')[1]) )* 60

    # Negative offset
    elif ('-') in time:
        time, offset = time.split('-')
        offset_s = -1 * (int(offset.split(':')[0])*60 + int(offset.split(':')[1])) * 60

    # Naive
    else:  
        offset_s = None

    # Handle time
    hour, minute, second = time.split(':')

    # Now parse date
    year, month, day = date.split('-') 

    # Convert everything to int
    year    = int(year)
    month   = int(month)
    day     = int(day)
    hour    = int(hour)
    minute  = int(minute)
    if '.' in second:
        usecond = int(second.split('.')[1])
        second  = int(second.split('.')[0])
    else:
        second  = int(second)
        usecond = 0

    return dt(year, month, day, hour, minute, second, usecond, tz=tz, naive=True if not tz else False, offset_s=offset_s)


def str_from_dt(dt):
    """Return the a string representation of a datetime object (as IS08601)."""
    return dt.isoformat()


def is_numerical(item):
    """Check if the argument is numerical."""
    if isinstance(item, float):
        return True
    if isinstance(item, int):
        return True
    try:
        # Cover other numerical types as Pandas (i.e. int64), Postgres (Decimal) etc.
        item + 1
        return True
    except:
        return False

# To acces the dt function even if an argument
# of a function is named "dt".
__dt = dt

