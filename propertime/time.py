# -*- coding: utf-8 -*-
"""Time and TimeSpan classes"""

import re
import math
import pytz
import copy
from datetime import datetime, timedelta
from dateutil.tz.tz import tzoffset
from .utilities import dt, timezonize, dt_from_s, s_from_dt, dt_from_str, now_s, str_from_dt, \
                       get_tz_offset, is_numerical, is_dt_inconsistent, is_dt_ambiguous_without_offset, \
                       correct_dt_dst, get_offset_from_dt
from .exceptions import ConsistencyError

# Setup logging
import logging
logger = logging.getLogger(__name__)


class Time(float):
    """A time object, as a floating point number corresponding to the number of seconds after the zero on the time axis.
    This is commonly known as Epoch, and set to 1st January 1970 UTC. Any other representations (as calendar time,
    time zones and daylight saving times) are built on top of it.

    It can be initialized in three main ways:

        * ``Time()``: if no arguments are given, then time is set to now;
        * ``Time(1703517120.3)``: it the argument is a number, it is treated as Epoch seconds;
        * ``Time(2023,5,6,13,45)``: if there is more than one argument, a datetime-like mode is
          used, with year, month, day, hour and second components all mandatory and in this order.

    In all three cases, by default the time is assumed on UTC. To create a time instance on a specific time zone,
    or with a specific UTC offset, you can use their respective keyword arguments ``tz`` and ``offset``. Sub-second precision
    for the datetime-like initialization mode can be achieved by setting a floating point value to the seconds component.
    Time can also be initialized using its string representation: ``Time(str(Time(2023,5,6,13,45, tz='US/Eastern'))`` will
    instantiate a time object equivalent to the original one.

    The initialization in case of ambiguous or not-existent time specifications generates an error:
    ``Time(2023,11,5,1,15, tz='US/Eastern')`` is ambiguous as there are "two" 1:15 AM on DST change on time zone
    US/Eastern, and ``Time(2023,3,12,2,30, tz='US/Eastern')`` just does not exists on such time zone. Creating time
    objects form an ambiguous time specification can be forced by enabling the "guessing" mode (``guessing=True``), but
    it will only be possible to create one of the two. To address this issue, use Epoch seconds or provide an UTC offset.

    Args:
        *args: the time value, either as seconds (float), datetime-like components (year, month, day, hour, minute, second)
            or string representation. If no value is given, then time is set to now.
        tz (:obj:`str`, :obj:`tzinfo`): the time zone, either as string representation or tzinfo object (including pytz and
          ZoneInfo). Defaults to 'UTC'.
        offset (:obj:`float`, :obj:`int`): the offset, in seconds, with respect to UTC. Defaults to 'auto', which sets it accordingly
            to the time zone. If set explicitly, it has to be consistent with the time zone, or the time zone has to be set to None.
        guessing (:obj:`bool`): if to enable guessing mode in case of ambiguous time specifications. Defaults to False.
    """

    def __new__(cls, *args, tz='UTC', offset='auto', guessing=False):

        # Timezonize the time zone
        tz = timezonize(tz)

        # Check offset and ensure as seconds
        if offset != 'auto' and offset is None:
            raise ValueError('Offset cannot be None if set')
        if offset != 'auto' and isinstance(offset, tzoffset):
            raise NotImplementedError('offsets as tzoffsets not implemented yet')
            #offset = get_offset_from_tzoffset()

        # Handle no arguments: current time
        if len(args) == 0:
            s = now_s()

        # Handle single argument case: Time as string or float
        elif len(args) == 1:

            # Time as string representation 
            if isinstance(args[0], str):
                embedded_tz = None
                embedded_offset = None

                # Parse, e.g. "Time: 1698537600.0 (2023-10-29 02:00:00 Europe/Rome DST)"
                try:
                    parts = args[0].replace('(','').replace(')','').split(' ')
                    s = float(parts[1])
                    tz_or_offset = parts[4]
                except IndexError:
                    raise ValueError('Unknow Time string format "{}"'.format(args[0])) from None
                try:
                    embedded_tz = timezonize(tz_or_offset)
                except:
                    offset_as_datetime = datetime.strptime(tz_or_offset[1:],'%H:%M')
                    offset_as_timedelta = timedelta(hours=offset_as_datetime.hour, minutes=offset_as_datetime.minute)
                    if tz_or_offset.startswith('+'):
                        offset_sign = 1
                    elif tz_or_offset.startswith('-'):
                        offset_sign = -1
                    else:
                        raise ValueError('Unknow Time string format "{}"'.format(args[0])) from None
                    embedded_offset = offset_as_timedelta.total_seconds() * offset_sign

                # Ensure consistency now
                if args[0] != str(Time(s, tz=embedded_tz, offset=embedded_offset if embedded_offset is not None else 'auto')):
                    raise ValueError('Inconsistent Time string format "{}"'.format(args[0])) from None

            # Time as float
            else:
                try:
                    s = float(args[0])
                except:
                    raise ValueError('Don\'t know how to create Time from "{}" of type "{}"'.format(args[0], args[0].__class__.__name__)) from None


        # Handle datetime-like init
        elif len(args) > 0:
            if len(args) < 6:
                raise ValueError('In this init mode you must provide all the components: year, month, day, hour, minute, second')
            elif len(args) == 7:
                raise ValueError('Got a 7th unexpected argument. If you are trying to set microseconds, use a floating point seconds value.')
            elif len(args) > 7:
                raise ValueError('Got too many argument, expected 6 (plus optional keyword-arguments)')

            # Handle sub-second precision
            if (isinstance(args[5], float) and not args[5].is_integer()):
                decimals = args[5] - math.floor(args[5])
                args = (args[0], args[1], args[2], args[3], args[4], math.floor(args[5]))
            else:
                decimals = 0

            try:
                if tz is not None:
                    s = s_from_dt(dt(*args, tz=tz, guessing=guessing)) + decimals
                elif offset != 'auto':
                    s = s_from_dt(dt(*args, tz=tzoffset(None, offset))) + decimals
                else:
                    raise ConsistencyError('No time zone nor offset set?')

            except ValueError as e:
                # TODO: improve this? e.g. AmbiguousValueError?
                if 'ambiguous' in str(e):

                    # Can we use the offset to remove the ambiguity?
                    if offset != 'auto':
                        s = s_from_dt(dt(*args, tz=tzoffset(None, offset), guessing=guessing)) + decimals
                    else:
                        raise ValueError('{}. Use guessing=True to allow creating it with a guess.'.format(e)) from None
                else:
                    raise e from None

        # Ok, now create the new instance as float
        time_instance = super().__new__(cls, s)

        # Handle time zone and offset
        if tz is not None:

            # Set the time zone and compute the offset from the time zone
            time_instance._tz = tz
            _dt = dt_from_s(s, tz=time_instance._tz)
            sign = -1 if _dt.utcoffset().days < 0 else 1
            if sign >0:
                _offset =  _dt.utcoffset().seconds
            else:
                _offset =  -((24*3600) - _dt.utcoffset().seconds)
            time_instance._offset = _offset

            # If there was also an offset set, check consistency:
            if offset != 'auto':
                if time_instance._offset != offset:
                    raise ValueError('An offset of {} for this time instance is inconsistent with its time zone "{}" '.format(offset, tz) + 
                                     '(which requires it to be {}). Please explicitly disable the time zone with tz=None.'.format(time_instance._offset))
        else:
            # Set only the offset
            time_instance._tz = None
            time_instance._offset = offset

        return time_instance

    def __repr__(self):

        self_as_float = float(self)
        decimal_part = str(self_as_float).split('.')[1]

        if self.tz:
            tz_or_offset = self.tz
            has_dst = True if self.to_dt().dst().total_seconds() else False
            dst_str = ' DST' if has_dst else ''

        else:
            # TODO: move to a _get_utc_offset() support function. Used also in dt().
            iso_time_part = self.to_iso().split('T')[1]
            if '+' in iso_time_part:
                tz_or_offset = '+'+iso_time_part.split('+')[1]
            else:
                tz_or_offset = '-'+iso_time_part.split('-')[1]
            dst_str = ''

        if decimal_part == '0':
            return ('Time: {} ({} {}{})'.format(self_as_float, self.to_dt().strftime('%Y-%m-%d %H:%M:%S'), tz_or_offset, dst_str))
        else:
            return ('Time: {} ({}.{} {}{})'.format(self_as_float, self.to_dt().strftime('%Y-%m-%d %H:%M:%S'), decimal_part, tz_or_offset, dst_str))

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _get_target_tz_and_offset(first, second):

        target_tz = None
        target_offset = 'auto'

        if isinstance(second, first.__class__):
            # Both have a time zone: they have to be the same
            if first.tz and second.tz:
                if first.tz != second.tz:
                    raise ValueError('Operating on time objects on different time zones would make the resulting time zone not defined')
                else:
                    target_tz = first.tz

            # Only one has a time zone: that wins
            if first.tz or second.tz:
                if first.tz:
                    target_tz = first.tz
                else:
                    target_tz = second.tz

            # Both have only an offset: they must be the same.
            if not first.tz and not second.tz:
                if first.offset != second.offset:
                    raise ValueError('Operating on time objects with no time zone and different offsets would make the resulting offset not defined')
                else:
                    target_offset = first.offset

        elif isinstance(second, datetime):
            if not second.tzinfo:
                raise ValueError('Cannot operate with naive datetimes')

            if isinstance(second.tzinfo, tzoffset):
                second_offset = get_offset_from_dt(second)
                second_tz = None
            else:
                second_offset = None
                second_tz = second.tzinfo

            # Both have a time zone: they have to be the same
            if first.tz and second_tz:
                if first.tz != second_tz:
                    raise ValueError('Operating on time/datetime objects on different time zones would make the resulting time zone not defined')
                else:
                    target_tz = first.tz

            # Only one has a time zone: that wins
            if first.tz or second_tz:
                if first.tz:
                    target_tz = first.tz
                else:
                    target_tz = second_tz

            # Both have only an offset: they must be the same.
            if not first.tz and not second_tz:
                if first.offset != second_offset:
                    raise ValueError('Operating on time/datetime objects with no time zone and different offsets would make the resulting offset not defined')
                else:
                    target_offset = first.offset

        return target_tz, target_offset

    def _operation(self, other, caller):

        def compute(first, second, caller):

            # Normal operations
            if caller == self.__add__:
                return first + second
            elif caller == self.__sub__:
                return first - second
            elif caller == self.__mul__:
                return first * second
            elif caller == self.__truediv__:
                return first / second
            elif caller == self.__mod__:
                return first % second
            elif caller == self.__pow__:
                return first ** second
            elif caller == self.__floordiv__:
                return first // second

            # Right operations
            elif caller == self.__radd__:
                return second + first
            elif caller == self.__rsub__:
                return second - first
            elif caller == self.__rmul__:
                return second * first
            elif caller == self.__rtruediv__:
                return second / first
            elif caller == self.__rmod__:
                return second % first
            elif caller == self.__rpow__:
                return second ** first
            elif caller == self.__rfloordiv__:
                return second // first

        if isinstance(other, self.__class__):
            target_tz, target_offset = self._get_target_tz_and_offset(self, other)
            target_value = compute(float(self), float(other), caller)

        elif isinstance(other, datetime):
            target_tz, target_offset = self._get_target_tz_and_offset(self, other)
            target_value = compute(float(self), s_from_dt(other), caller)

        elif isinstance(other, TimeSpan):
            return NotImplemented

        elif isinstance(other, timedelta):
            return NotImplemented

        else:
            target_tz, target_offset = self.tz, self.offset
            target_value = compute(float(self),other, caller)

        return Time(target_value, tz=target_tz, offset=target_offset)

    def __add__(self, other):
        return self._operation(other, self.__add__)

    def __sub__(self, other):
        return self._operation(other, self.__sub__)

    def __mul__(self, other):
        return self._operation(other, self.__mul__)

    def __truediv__(self, other):
        return self._operation(other, self.__truediv__)

    def __mod__(self, other):
        return self._operation(other, self.__mod__)

    def __pow__(self, other):
        return self._operation(other, self.__pow__)

    def __floordiv__(self, other):
        return self._operation(other, self.__floordiv__)

    def __radd__(self, other):
        return self._operation(other, self.__radd__)

    def __rsub__(self, other):
        return self._operation(other, self.__rsub__)

    def __rmul__(self, other):
        return self._operation(other, self.__rmul__)

    def __rtruediv__(self, other):
        return self._operation(other, self.__rtruediv__)

    def __rmod__(self, other):
        return self._operation(other, self.__rmod__)

    def __rpow__(self, other):
        return self._operation(other, self.__rpow__)

    def __rfloordiv__(self, other):
        return self._operation(other, self.__rfloordiv__)

    @classmethod
    def from_dt(cls, dt, tz='auto', offset='auto', guessing=False):
        """Create a Time object form a datetime. If naive, then a time zone or an offset is required.

        Please note that tz and offset arguments, if set to something else than "auto" when using a
        timezone-aware (or offset-aware) datetime, will "move" it to the given time zone or offset.

        For example, ``Time.from_dt(dt(2023,5,6,13,45, tz='US/Eastern'), tz='Europe/Rome')`` will result
        in the Time object corresponding to 2023-05-06 19:45:00 Europe/Rome.

        Args:
            dt (:obj:`datetime`): the datetime from which to create the new Time object.
            tz (:obj:`str`, :obj:`tzinfo`): the time zone, either as string representation or tzinfo object. Defaults to 'UTC'.
            offset (:obj:`float`, :obj:`int`): the offset, in seconds, with respect to UTC. Defaults to 'auto', which sets it accordingly
                to the time zone. If set explicitly, it has to be consistent with the time zone, or the time zone has to be set to None.
            guessing (:obj:`bool`): if to enable guessing mode in case of ambiguous time specifications. Defaults to False.
        """

        # Set given time zone and offset
        given_offset = offset if offset != 'auto' else None
        given_tz = tz if  tz != 'auto' else None

        # Set embedded time zone and offset
        if not dt.tzinfo:
            embedded_offset = None
            embedded_tz = None
        else:
            if isinstance(dt.tzinfo, tzoffset):
                embedded_offset = get_offset_from_dt(dt)
                embedded_tz = None
            else:
                embedded_offset = None
                embedded_tz = dt.tzinfo

        # Handle naive datetime or extract time zone/offset
        if embedded_offset is None and embedded_tz is None:

            # Look at the tz argument if any, and decorate
            if given_tz is not None:
                dt = timezonize(given_tz).localize(dt)

            # Look at the offset argument if any, and decorate
            elif given_offset is not None:
                dt = pytz.UTC.localize(dt).replace(tzinfo = tzoffset(None, given_offset))

            # Otherwise, raise
            else:
                raise ValueError('Got a naive datetime, please set its time zone or offset')

            # Check for potential ambiguity
            if is_dt_ambiguous_without_offset(dt):
                dt_naive = dt.replace(tzinfo=None)
                if not guessing:
                    raise ValueError('Sorry, datetime {} is ambiguous on time zone {} without an offset'.format(dt_naive, dt.tzinfo))
                else:
                    # TODO: move to a _get_utc_offset() support function. Used also in Time __str__ and dt() in utilities
                    iso_time_part = str_from_dt(dt).split('T')[1]
                    if '+' in iso_time_part:
                        offset_assumed = '+'+iso_time_part.split('+')[1]
                    else:
                        offset_assumed = '-'+iso_time_part.split('-')[1]
                    logger.warning('Time {} is ambiguous on time zone {}, assuming {} UTC offset'.format(dt_naive, tz, offset_assumed))

        # Now convert the (always time zone or offset -aware) datetime to seconds
        s = s_from_dt(dt)

        target_offset = None
        target_tz = None

        # Set target time zone and offset
        if given_tz is not None:
            target_tz = given_tz
        else:
            if embedded_tz is not None:
                if given_offset is None:
                    target_tz = embedded_tz

        if given_offset is not None:
            if given_tz is None:
                target_offset = given_offset
        else:
            if embedded_offset is not None:
                if given_tz is None:
                    target_offset = embedded_offset

        # From "None" to "auto" (only for the offset)
        if target_offset is None:
            target_offset = 'auto'

        # ..and create the new object
        obj = cls(s, tz=target_tz, offset=target_offset)

        # Lastly, if both time zone and offset were given, check for consistency
        if given_tz is not None and given_offset is not None:
            if obj.offset != given_offset:
                raise ValueError('An offset of {} for this time instance is inconsistent with its time zone "{}" '.format(given_offset, target_tz) +
                                 '(which requires it to be {}). Please explicitly disable the time zone with tz=None.'.format(obj.offset))

        return obj

    @classmethod
    def from_iso(cls, iso, tz='auto', offset='auto'):
        """Create a Time object form an ISO 8601 string. If naive, then a time zone or an offset is required.

        Please note that tz and offset arguments, if set to something else than "auto" when using a
        UTC-aware (or offset-aware) ISO string, will "move" it to the given time zone or offset.

        For example, ``Time.from_iso('2023-12-25T16:12:00+01:00', tz='US/Eastern')`` will result
        in the Time object corresponding to 2023-12-25 10:12:00 US/Eastern.

        Args:
            dt (:obj:`datetime`): the datetime from which to create the new Time object.
            tz (:obj:`str`, :obj:`tzinfo`): the time zone, either as string representation or tzinfo object. Defaults to 'UTC'.
            offset (:obj:`float`, :obj:`int`): the offset, in seconds, with respect to UTC. Defaults to 'auto', which sets it accordingly
                to the time zone. If set explicitly, it has to be consistent with the time zone, or the time zone has to be set to None.
        """

        # Set given time zone and offset
        given_offset = offset if offset != 'auto' else None
        given_tz = tz if  tz != 'auto' else None

        # By default there is no embedded time zone or offset
        embedded_offset = None
        embedded_tz = None

        # Handle naive iso
        if not (iso[-1] == 'Z' or '+' in iso or ('-' in iso and '-' in iso.split('T')[1])):

            # Look at the tz argument if any, and use it
            if given_tz:
                dt = dt_from_str(iso, tz=given_tz)

            # Look at the offset argument if any, and use it
            elif given_offset is not None:
                dt = dt_from_str(iso, tz=tzoffset(None, given_offset))

            # Otherwise, raise
            else:
                raise ValueError('Got a naive ISO string, please set its time zone or offset')

        else:
            dt = dt_from_str(iso)

            # Handle embedded time zone (only Zulu, which is UTC) or offset
            if iso[-1] == 'Z':
                embedded_tz = pytz.UTC
            else:
                embedded_offset = dt.utcoffset().seconds

        # Now convert the (always time zone or offset -aware) datetime to seconds
        s = s_from_dt(dt)

        target_offset = None
        target_tz = None

        # Set target time zone and offset
        if given_tz is not None:
            target_tz = given_tz
        else:
            if embedded_tz is not None:
                if given_offset is None:
                    target_tz = embedded_tz

        if given_offset is not None:
            if given_tz is None:
                target_offset = given_offset
        else:
            if embedded_offset is not None:
                if given_tz is None:
                    target_offset = embedded_offset

        # From "None" to "auto" (only for the offset)
        if target_offset is None:
            target_offset = 'auto'

        # ..and create the new object
        obj = cls(s, tz=target_tz, offset=target_offset)

        # Lastly, if both time zone and offset were given, check for consistency
        if given_tz is not None and given_offset is not None:
            if obj.offset != given_offset:
                raise ValueError('An offset of {} for this time instance is inconsistent with its time zone "{}" '.format(given_offset, target_tz) +
                                 '(which requires it to be {}). Please explicitly disable the time zone with tz=None.'.format(obj.offset))

        return obj

    def to_dt(self):
        """Return time as a datetime object."""
        try:
            return self._dt
        except AttributeError:
            try:
                if self.tz:
                    self._dt = dt_from_s(self, tz=self.tz)
                else:
                    self._dt = dt_from_s(self, tz=tzoffset(None, self.offset))
                return self._dt
            except Exception as e:
                raise e.__class__('{} (time as float: "{}", offset: "{}", tz: "{}")'.format(e, float(self), self.offset, self.tz)) from None

    def to_iso(self):
        """Return time as a string in ISO 8601 format."""
        return str_from_dt(self.to_dt())

    @property
    def tz(self):
        """The time zone of the time. If this was set with a string (including the default 'UTC' value), then
        this is a pytz object. Otherwise, it is the exact same object used for the tz argument, assuming it 
        was a valid tzinfo (e.g. a ZoneInfo)."""
        return self._tz

    @property
    def offset(self):
        """The (UTC) offset of the time, in seconds."""
        return self._offset

    def as_tz(self, tz):
        """Get this time on another time zone."""

        new_obj = copy.deepcopy(self)
        new_obj._tz = tz

        # Reset dt cache if present
        try:
            del new_obj._dt
        except AttributeError:
            pass

        # Set the offset accordingly to the time zone
        sign = -1 if new_obj.to_dt().utcoffset().days < 0 else 1
        new_obj._offset = sign * new_obj.to_dt().utcoffset().seconds

        return new_obj

    def as_offset(self, offset):
        """Get this time with another (UTC) offset."""

        new_obj = copy.deepcopy(self)
        new_obj._offset = offset

        # Reset dt cache
        try:
            del new_obj._dt
        except AttributeError:
            pass

        # Unset the time zone
        new_obj._tz = None

        return new_obj

    def is_integer(self):
        """Return True if time is an integer, i.e. it has no or zero sub-seconds."""
        return super().is_integer()

    def as_integer_ratio(self):
        """Return time as integer ratio."""
        return super().as_integer_ratio()

    @classmethod
    def fromhex(cls, string):
        """Create time from a hexadecimal string."""
        return cls(float.fromhex(string))

    def hex(self):
        """Return a hexadecimal representation of time."""
        return super().hex()

    def conjugate(self):
        """Disabled. It does not make sense to use imaginary numbers with time."""
        raise NotImplementedError('It does not make sense to use imaginary numbers with time')

    def imag(self):
        """Disabled. It does not make sense to use imaginary numbers with time."""
        raise NotImplementedError('It does not make sense to use imaginary numbers with time')

    def real(self):
        """Disabled. It does not make sense to use imaginary numbers with time."""
        raise NotImplementedError('It does not make sense to use imaginary numbers with time')


class TimeSpan:
    """A time span object, that can have either fixed or variable length (duration). Whether this is variable
    or not, it depends if there are any calendar time components involved (years, months, weeks and days).

    Time spans support many operations, and can be added and subtracted with numerical values, Propertime's time
    objects, datetime objects, as well as other time spans.

    Their initialization supports both string representations and explicitly setting the various
    components: years, months, weeks, days, hours, minutes and seconds. Sub-second precision can be achieved
    by using a floating point value for the seconds component.

    In the string representation, the mapping is as follows:

        * ``'Y': 'years'``
        * ``'M': 'months'``
        * ``'W': 'weeks'``
        * ``'D': 'days'``
        * ``'h': 'hours'``
        * ``'m': 'minutes'``
        * ``'s': 'seconds'``

    For example, to create a time span of one hour, the following four are equivalent:

    .. code-block:: python

        TimeSpan('1h') == TimeSpan('3600s') == TimeSpan(seconds=3600) == TimeSpan(hours=1)

    The first two use the string representation, while the third and the fourth explicitly
    set its components (hours and seconds, in this case).

    To get the time span length, or duration, you can use the ``as_seconds()`` method:

    .. code-block:: python

        TimeSpan('1h').as_seconds()

    However, as soon as a calendar time component kicks in, the time span length becomes variable: a time span of
    one day can last for 23, 24 or 24 hours (and thus 82800, 86400 and 90000 seconds) depending on DST changes.
    Similarly, a month can have 28, 29, 30 or 31 days; and a year can have both 365 and 366 days.

    Note indeed that:

    .. code-block:: python

        TimeSpan('24h') != TimeSpan('1D')

    The length of a time span where one ore more calendar time components are involved is therefore well defined only
    if providing context about *when* it is applied:

    .. code-block:: python

        TimeSpan('1D').as_seconds(starting_at=some_time)

    This is automatically handled when using time spans to perform operations, so that for example to get to tomorow's
    same time of the day, you would just do:

    .. code-block:: python

        Time() + TimeSpan('1D')

    ...and the time span will take care of computing the correct calendar arithmetic, including the DST change.
    If you instead wanted to add exactly 24 hours, thus getting to a different time of the day if DST changed
    within the time span, you would have used:

    .. code-block:: python

        Time() + TimeSpan('24h')

    Lastly, when calendar time components are involved, there might be also some undefined or ambiguous operations.
    And exactly as it would happen if dividing a number by zero, they will cause an error:

    .. code-block:: python

        Time(2023,1,31) + TimeSpan(months=1)
        # Error, the 31st of February does not exist

        Time(2023,3,25,2,15,0, tz='Europe/Rome') + TimeSpan(days=1)
        # Error, the 2:15 AM does not exist on Europe/Rome in the target day

        Time(2023,10,28,2,15,0, tz='Europe/Rome') + TimeSpan(days=1)
        # Error, there are two 2:15 AM on Europe/Rome in the target day


    Args:
        value (:obj:`str`): the time span value as string representation.
        years (:obj:`int`): the time span years component.
        weeks (:obj:`int`): the time span weeks component.
        months (:obj:`int`): the time span weeks component.
        days(:obj:`int`): the time span days component.
        hours (:obj:`int`): the time span hours component.
        minutes (:obj:`int`): the time span minutes component.
        seconds (:obj:`int`, :obj:`float`): the time span seconds, as float to include sub-second precision (up to the microsecond).
    """

    # NOT ref to https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes :  %d, %m, %w %y - %H, %M, %S
    # Instead: M, D, Y, W - h m s

    _mapping_table = { 
                       'Y': 'years',
                       'M': 'months',
                       'W': 'weeks',
                       'D': 'days',
                       'h': 'hours',
                       'm': 'minutes',
                       's': 'seconds',
                      }

    def __init__(self, value=None, years=0, weeks=0, months=0, days=0, hours=0, minutes=0, seconds=0):

        # Value OR explicit time components
        if value and (years or months or days or hours or minutes or seconds):
            raise ValueError('Choose between string init and explicitly setting years, months, days, hours minutes or seconds.')

        # Handle second/microsecond
        if isinstance(seconds, float):
            if  seconds.is_integer():
                seconds = int(seconds)
                _int_seconds = seconds
                _int_microseconds = 0
            else:
                _int_seconds = int(math.floor(seconds))
                _int_microseconds = int((seconds-int(math.floor(seconds)))*1000000)
        else:
            _int_seconds = int(seconds)
            _int_microseconds = 0

        # Set the time components
        self.years = years
        self.months = months
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes 
        self.seconds = seconds
        self._int_seconds = _int_seconds
        self._int_microseconds = _int_microseconds

        # Handle string value
        if value:
            if isinstance(value,str):

                # Parse the value (as string), first handle seconds and microseconds special case
                if value.endswith('s'):

                    # Get the value as clena string ( 
                    if '_' in value:
                        value_seconds = value.split('_')[-1][:-1]
                    else:
                        value_seconds = value[:-1]

                    if '.' in value_seconds and not float(value_seconds).is_integer():
                        # Ensure we can handle precision
                        value_decimal_seconds = value_seconds.split('.')[1][0:-1] 
                        if len(value_decimal_seconds) > 6:
                            raise ValueError('Sorry, "{}" has too many decimal seconds to be handled with a TimeSpan (which supports precision up to the microsecond).'.format(value))

                        # Set
                        self.seconds = float(value_seconds)
                        self._int_seconds = int(math.floor(self.seconds))
                        self._int_microseconds = int((self.seconds-int(math.floor(self.seconds)))*1000000)

                    else:
                        self.seconds = int(float(value_seconds))
                        self._int_seconds  = self.seconds
                        self._int_microseconds = 0

                    # Was it composite? If so, redefine value withiut seconds
                    if '_' in value:
                        values_without_seconds = value.split('_')[:-1]
                    else:
                        values_without_seconds = []
                else:
                    values_without_seconds = value.split('_')

                if values_without_seconds:

                    # Parse value using regex
                    regex = re.compile('^([0-9]+)([YMDWhm]{1,2})$')
                    for value in values_without_seconds:
                        try:
                            groups = regex.match(value).groups()
                        except AttributeError:
                            raise ValueError('Cannot parse string representation for the TimeSpan, unknown format ("{}")'.format(value)) from None

                        setattr(self, self._mapping_table[groups[1]], int(groups[0]))

                if not self.years and not self.months and not self.weeks and not self.days and not self.hours and not self.minutes and not self.seconds:
                    raise ValueError('Dont\'t know hot to create a TimeSpan from value "{}" of type {}'.format(value, value.__class__.__name__))
            else:
                raise ValueError('Dont\'t know hot to create a TimeSpan from value "{}" of type {}'.format(value, value.__class__.__name__))

    def __repr__(self):
        string = ''
        if self.years: string += str(self.years)               + 'Y' + '_'
        if self.months: string += str(self.months)             + 'M' + '_'
        if self.weeks: string += str(self.weeks)               + 'W' + '_'
        if self.days: string += str(self.days)                 + 'D' + '_'
        if self.hours: string += str(self.hours)               + 'h' + '_'
        if self.minutes: string += str(self.minutes)           + 'm' + '_'
        if self.seconds: string += str(self.seconds)           + 's' + '_'

        string = string[:-1]
        return string

    def __str__(self):
        return self.__repr__()

    def __radd__(self, other):
        if isinstance(other, self.__class__):  
            return TimeSpan(years        = self.years + other.years,
                            months       = self.months + other.months,
                            weeks        = self.weeks + other.weeks,
                            days         = self.days + other.days,
                            hours        = self.hours + other.hours,
                            minutes      = self.minutes + other.minutes,
                            seconds      = self.seconds + other.seconds)

        elif isinstance(other, datetime):
            if not other.tzinfo:
                raise ValueError('Timezone of the datetime to sum with is required')
            return self.shift(other, times=1)

        elif isinstance(other, Time):
            return Time.from_dt(self.shift(other.to_dt(), times=1))

        elif is_numerical(other):
            return other + self.as_seconds()

        else:
            raise NotImplementedError('Adding TimeSpans with objects of class "{}" is not implemented'.format(other.__class__.__name__))

    def __add__(self, other):

        if isinstance(other, self.__class__):
            return self.__radd__(other)
        else:
            raise NotImplementedError('Cannot add anything (except another TimeSpan) to a TimeSpan. Only a TimeSpan to something else.')

    def __rsub__(self, other):

        if isinstance(other, self.__class__):
            raise NotImplementedError('Subtracting a TimeSpan from another TimeSpan is not implemented to prevent negative TimeSpans.')

        elif isinstance(other, datetime):
            if not other.tzinfo:
                raise ValueError('Timezone of the datetime to sum with is required')
            return self.shift(other, times=-1)

        elif isinstance(other, Time):
            return Time(self.shift(other.to_dt(), times=-1))

        elif is_numerical(other):
            return other - self.as_seconds()

        else:
            raise NotImplementedError('Subtracting TimeSpans with objects of class "{}" is not implemented'.format(other.__class__.__name__))

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            raise NotImplementedError('Subtracting a TimeSpan from another TimeSpan is not implemented to prevent negative TimeSpans.')
        else:
            raise NotImplementedError('Cannot subtract anything from a TimeSpan. Only a TimeSpan from something else.')

    def __truediv__(self, other):
        raise NotImplementedError('Division for TimeSpans is not implemented')

    def __rtruediv__(self, other):
        raise NotImplementedError('Division for TimeSpans is not implemented')

    def __mul__(self, other):
        raise NotImplementedError('Multiplication for TimeSpans is not implemented')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):

        # Check against another TimeSpan
        if isinstance(other, TimeSpan):

            try:
                # First of all check with the duration as seconds
                if self.as_seconds() == other.as_seconds():
                    return True
                else:
                    return False
            except:
                pass

            # Check using the calendar components
            if self.years != other.years:
                return False
            if self.months != other.months:
                return False
            if self.weeks != other.weeks:
                return False
            if self.days != other.days:
                return False
            if self.hours != other.hours:
                return False
            if self.minutes != other.minutes:
                return False
            if self.seconds != other.seconds:
                return False
            return True

            # Check using the duration in seconds (if defined), as 15m and 900s are actually the same span
            try:
                if self.as_seconds() == other.as_seconds():
                    return True
            except ValueError:
                pass

        # Check for direct equality with string representation
        if str(self) == other:
            return True

        # Check for duration as seconds equality, i.e. comparing with a float
        try:
            if self.as_seconds() == other:
                return True
        except (TypeError, ValueError):
            pass

        # If everything fails, return false:
        return False

    def _is_composite(self):
        components = 0
        for item in self._mapping_table:
            if getattr(self, self._mapping_table[item]):
                components +=1
        if components > 1:
            return True
        else:
            return False

    def round(self, time, how='half'):
        """Round a time or datetime object according to this TimeSpan."""

        if self._is_composite():
            raise ValueError('Sorry, only simple TimeSpans are supported by the round operation')

        if isinstance(time, Time):
            time_dt = time.to_dt()
        else:
            time_dt = time

        if not time_dt.tzinfo:
            raise ValueError('The timezone of the Time or datetime is required')

        # Handle calendar/physical time components
        if self.years or self.months or self.weeks or self.days:

            if self.years:
                if self.years > 1:
                    raise NotImplementedError('Cannot round based on calendar TimeSpans with years > 1')
                floored_dt=time_dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            if self.months:
                if self.months > 1:
                    raise NotImplementedError('Cannot round based on calendar TimeSpans with months > 1')
                floored_dt=time_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if self.weeks:
                # Get to this day midnight
                floored_dt = TimeSpan('1D').floor(time_dt)

                # If not monday, subtract enought days to get there
                if floored_dt.weekday() != 0:
                    floored_dt = floored_dt - timedelta(days=floored_dt.weekday())

            if self.days:
                if self.days > 1:
                    raise NotImplementedError('Cannot round based on calendar TimeSpans with days > 1')
                floored_dt=time_dt.replace(hour=0, minute=0, second=0, microsecond=0)

            # Check DST offset consistency and fix if not respected
            if is_dt_inconsistent(floored_dt):
                floored_dt = correct_dt_dst(floored_dt)

            # Get the required rounding
            if how == 'floor':
                rounded_dt = floored_dt

            elif how == 'ceil':
                ceiled_dt = self.shift(floored_dt, 1)
                rounded_dt = ceiled_dt

            elif how == 'half':
                ceiled_dt = self.shift(floored_dt, 1)
                distance_from_time_floor_s = abs(s_from_dt(time_dt) - s_from_dt(floored_dt)) # Distance from floor
                distance_from_time_ceil_s  = abs(s_from_dt(time_dt) - s_from_dt(ceiled_dt))  # Distance from ceil

                if distance_from_time_floor_s <= distance_from_time_ceil_s:
                    rounded_dt = floored_dt
                else:
                    rounded_dt = ceiled_dt
            else:
                raise ValueError('Unknown rounding strategy "{}"'.format(how))

        else:

            # Convert input time to seconds
            time_s = s_from_dt(time_dt)
            tz_offset_s = get_tz_offset(time_dt)

            # Get TimeSpan duration in seconds
            time_span_s = self.as_seconds(time_dt)

            # Apply modular math (including timezone time translation trick if required (multiple hours))
            # TODO: check for correctness, the time shift should be always done...

            if self.hours > 1 or self.minutes > 60:
                time_floor_s = ( (time_s - tz_offset_s) - ( (time_s - tz_offset_s) % time_span_s) ) + tz_offset_s
            else:
                time_floor_s = time_s - (time_s % time_span_s)

            time_ceil_s   = time_floor_s + time_span_s

            if how == 'floor':
                time_rounded_s = time_floor_s

            elif how == 'ceil':
                time_rounded_s = time_ceil_s

            else:
                distance_from_time_floor_s = abs(time_s - time_floor_s) # Distance from floor
                distance_from_time_ceil_s  = abs(time_s - time_ceil_s)  # Distance from ceil

                if distance_from_time_floor_s <= distance_from_time_ceil_s:
                    time_rounded_s = time_floor_s
                else:
                    time_rounded_s = time_ceil_s

            rounded_dt = dt_from_s(time_rounded_s, tz=time_dt.tzinfo)

        # Return
        if isinstance(time, Time):
            return Time.from_dt(rounded_dt)
        else:
            return rounded_dt

    def floor(self, time):
        """Floor a time or datetime object according to this time span."""
        return self.round(time, how='floor')

    def ceil(self, time):
        """Ceil a time or datetime object according to this time span."""
        return self.round(time, how='ceil')

    def shift(self, time, times=1):
        """Shift a given time or datetime object of n times this time span."""
        if self._is_composite():
            raise ValueError('Sorry, only simple TimeSpans are supported by the shift operation')
 
        if isinstance(time, Time):
            time_dt = time.to_dt()
        else:
            time_dt = time
 
        # Convert input time to seconds
        time_s = s_from_dt(time_dt)

        # Handle calendar/physical time components
        if self.years or self.months or self.weeks or self.days:

            if times != 1:
                raise NotImplementedError('Cannot shift calendar TimeSpans for times greater than 1 (got times="{}")'.format(times))

            # Create a TimeDelta object for everything but years and months
            delta = timedelta(weeks = self.weeks,
                              days = self.days,
                              hours = self.hours,
                              minutes = self.minutes,
                              seconds = self._int_seconds,
                              microseconds = self._int_microseconds)

            # Apply the time delta for the shift
            time_shifted_dt = time_dt + delta

            # Handle years
            if self.years:
                time_shifted_dt = time_shifted_dt.replace(year=time_shifted_dt.year + self.years)

            # Handle months
            if self.months:

                tot_months = self.months + time_shifted_dt.month
                years_to_add = math.floor(tot_months/12.0)
                new_month = (tot_months % 12 )
                if new_month == 0:
                    new_month=12
                    years_to_add = years_to_add -1

                time_shifted_dt = time_shifted_dt.replace(year=time_shifted_dt.year + years_to_add)
                try:
                    time_shifted_dt = time_shifted_dt.replace(month=new_month)
                except ValueError as e:
                    raise ValueError('{} for {} plus {} month(s)'.format(e, time_shifted_dt, self.months).capitalize())

            # Check DST offset consistency and fix if not respected
            if is_dt_inconsistent(time_shifted_dt):
                try:
                    time_shifted_dt = correct_dt_dst(time_shifted_dt)
                except ValueError as e:
                    # If we are here, it means that the datetime cannot be corrected.
                    # This basically means that we are in the edge case where we ended
                    # up in a a non-existent datetime, e.g. 2023-03-26 02:15 on Europe/Rome,
                    # probably by adding a calendar time span to a previous datetime
                    raise ValueError('Cannot shift "{}" by "{}" ({})'.format(time_dt,self,e)) from None

            # Check if we ended up on an ambiguous time
            if is_dt_ambiguous_without_offset(time_shifted_dt):
                time_shifted_dt_naive =  time_shifted_dt.replace(tzinfo=None)
                raise ValueError('Cannot shift "{}" by "{}" (Would end up on time {} which is ambiguous on time zone {})'.format(time_dt,self,time_shifted_dt_naive, time_shifted_dt.tzinfo)) from None

        else:
            # Get duration (seconds)
            time_span_s = self.as_seconds()

            time_shifted_s = time_s + ( time_span_s * times )
            time_shifted_dt = dt_from_s(time_shifted_s, tz=time_dt.tzinfo)

            return time_shifted_dt

        # Return
        if isinstance(time, Time):
            return Time.from_dt(time_shifted_dt)
        else:
            return time_shifted_dt

    def as_seconds(self, starting_at=None):
        """The length (duration) of the time span, in seconds."""

        start = starting_at

        if start and isinstance(start, Time):
            start = start.to_dt()

        # Handle calendar/physical time components
        if self.years or self.months or self.weeks or self.days:

            if not start:
                raise ValueError('You can ask to get a calendar TimeSpan as seconds only if you provide the span starting point')

            if self._is_composite():
                raise ValueError('Sorry, only simple TimeSpans are supported by this operation')

            # Start Epoch
            start_epoch = s_from_dt(start)

            # End epoch
            end_dt = self.shift(start, 1)
            end_epoch = s_from_dt(end_dt)

            # Get duration based on seconds
            time_span_s = end_epoch - start_epoch

        else:

            time_span_s = 0
            if self.hours:
                time_span_s += self.hours * 60 * 60
            if self.minutes:
                time_span_s += self.minutes * 60
            if self.seconds:
                time_span_s += self.seconds

        # Return
        return float(time_span_s)

