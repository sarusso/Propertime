# -*- coding: utf-8 -*-
"""Time classes"""

import re
import math
import pytz
from datetime import datetime, timedelta
from dateutil.tz.tz import tzoffset
from .utils import dt, timezonize, dt_from_s, s_from_dt, dt_from_str, now_s, str_from_dt, \
                   get_tz_offset, is_numerical, is_dt_inconsistent, is_dt_ambiguous_without_offset, \
                   correct_dt_dst
from .exceptions import ConsistencyError

# Setup logging
import logging
logger = logging.getLogger(__name__)


class Time(float):

    def __new__(cls, value=None, *args, **kwargs):

        can_guess = kwargs.pop('can_guess', False)
        given_tz = timezonize(kwargs.pop('tz', None))
        given_offset = kwargs.pop('offset', None)
        embedded_tz = None
        embedded_offset = None

        # Handle value as datetime
        if isinstance(value, datetime):

            # Handle naive datetime if it is the case
            if not value.tzinfo:

                # Look at the tz argument if any, and decorate
                if given_tz:
                    value = timezonize(given_tz).localize(value)

                # Look at the offset argument if any, and decorate
                elif given_offset is not None:
                    value = pytz.UTC.localize(value).replace(tzinfo = tzoffset(None, given_offset))

                # Otherwise, treat as UTC
                else:
                    value = pytz.UTC.localize(value)

            # Now convert the (always timezone-aware) datetime
            if isinstance(value.tzinfo, tzoffset):
                embedded_offset = value.utcoffset().seconds
            else:
                embedded_tz = value.tzinfo
            value = s_from_dt(value)

        # Handle value as string
        if isinstance(value, str):

            # Handle naive string if it is the case
            if not (value[-1] == 'Z' or '+' in value or ('-' in value and '-' in value.split('T')[1])):

                # Look at the tz argument if any, and use it
                if given_tz:
                    converted_dt = dt_from_str(value, tz=given_tz)

                # Look at the offset argument if any, and use it
                elif given_offset is not None:
                    converted_dt = dt_from_str(value, tz=tzoffset(None, given_offset))

                # Otherwise, treat as UTC
                else:
                    converted_dt = dt_from_str(value+'Z')

            else:
                converted_dt = dt_from_str(value)

                # Handle embedded time zone (only Zulu, which is UTC) or offset 
                if value[-1] == 'Z':
                    embedded_tz = pytz.UTC
                else:
                    embedded_offset = converted_dt.utcoffset().seconds

            # Now convert the (always offset-aware) datetime converted from the string
            value = s_from_dt(converted_dt)


        # Handle no value -> current time
        elif value is None:
            value = now_s()

        else:
            # Detect classic datetime-like init
            if len(args) > 0:

                if given_tz:
                    # Time zone, set, check if also the offset was
                    if given_offset is not None:
                        value = s_from_dt(dt(value, *args, tz=tzoffset(None, given_offset), can_guess=can_guess).astimezone(given_tz))
                    else:
                        value = s_from_dt(dt(value, *args, tz=given_tz, can_guess=can_guess))

                elif given_offset is not None:
                    # Offset set
                    value = s_from_dt(dt(value, *args, tz=tzoffset(None, given_offset), can_guess=can_guess))

                else:
                    # Nothing set, treat as UTC
                    value = s_from_dt(dt(value, *args, tz='UTC', can_guess=can_guess))

            else:
                # Check float-compatible value type
                try:
                    float(value)
                except:
                    raise ValueError('Don\'t know how to create Time from "{}" of type "{}"'.format(value, value.__class__.__name__))

        # Create the new instance
        time_instance = super().__new__(cls, value)

        # Handle time zone & offset arguments. Can override "value" (string/datetime) ones.
        if kwargs:
            raise ValueError('Unhandled kwargs: {}'.format(kwargs))

        if given_tz or (embedded_tz is not None and given_offset is None):

            # Set time zone, and also the offset
            tz = given_tz if given_tz else embedded_tz
            time_instance._tz = timezonize(tz)
            _dt = dt_from_s(value, tz=time_instance._tz)
            sign = -1 if _dt.utcoffset().days < 0 else 1 
            time_instance._offset = sign * _dt.utcoffset().seconds

        elif given_offset is not None or (embedded_offset is not None and not given_tz):

            # Set only the offset
            offset = given_offset if given_offset is not None else embedded_offset
            time_instance._tz = None
            time_instance._offset = offset

        else:

            # Otherwise, default to UTC
            time_instance._tz = pytz.UTC
            time_instance._offset = 0

        return time_instance

    @property
    def tz(self):
        return self._tz

    @tz.setter
    def tz(self, value):
        self._tz = value

        # Reset dt cache if present
        try:
            del self._dt
        except AttributeError:
            pass

        # Set the offset accordingly to the time zone
        sign = -1 if self.dt().utcoffset().days < 0 else 1 
        self._offset = sign * self.dt().utcoffset().seconds

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

        # Reset dt cache
        try:
            del self._dt
        except AttributeError:
            pass

        # Unset the time zone
        self._tz = None

    def dt(self):
        try:
            return self._dt
        except AttributeError:
            if self.tz:
                self._dt = dt_from_s(self, tz=self.tz)
            else:
                self._dt = dt_from_s(self, tz=tzoffset(None, self.offset))
            return self._dt

    def iso(self):
        return str_from_dt(self.dt())

    def __str__(self):

        self_as_float = float(self)
        decimal_part = str(self_as_float).split('.')[1]

        if self.tz:
            tz_or_offset = self.tz
        else:
            # TODO: move to a _get_utc_offset() support function. Used also in dt().
            iso_time_part = self.iso().split('T')[1]
            if '+' in iso_time_part:
                tz_or_offset = '+'+iso_time_part.split('+')[1]
            else:
                tz_or_offset = '-'+iso_time_part.split('-')[1]

        if decimal_part == '0':
            return ('Time: {} ({} {})'.format(self_as_float, self.dt().strftime('%Y-%m-%d %H:%M:%S'), tz_or_offset))
        else:
            return ('Time: {} ({}.{} {})'.format(self_as_float, self.dt().strftime('%Y-%m-%d %H:%M:%S'), decimal_part, tz_or_offset))

    def __repr__(self):
        return self.__str__()



class TimeUnit:
    """A unit which can represent both physical (fixed) and calendar (variable) time units.
    Can handle precision up to the microsecond and can be added and subtracted with numerical
    values, Time and datetime objects, and other TimeUnits.

    Can be initialized both using a numerical value, a string representation, or by explicitly setting
    years, months, weeks, days, hours, minutes, seconds and microseconds. In the string representation,
    the mapping is as follows:

        * ``'Y': 'years'``
        * ``'M': 'months'``
        * ``'W': 'weeks'``
        * ``'D': 'days'``
        * ``'h': 'hours'``
        * ``'m': 'minutes'``
        * ``'s': 'seconds'``
        * ``'u': 'microseconds'``

    For example, to create a time unit of one hour, the following three are equivalent, where the
    first one uses the numerical value, the second the string representation, and the third explicitly
    sets the time component (hours in this case): ``TimeUnit('1h')``, ``TimeUnit(hours=1)``, or ``TimeUnit(3600)``.
    Not all time units can be initialized using the numerical value, in particular calendar time units which can
    have variable duration: a time unit of one day, or ``TimeUnit('1d')``, can last for 23, 24 or 24 hours depending
    on DST changes. On the contrary, a ``TimeUnit('24h')`` will always last 24 hours and can be initialized as
    ``TimeUnit(86400)`` as well. 

    Args:
        value: the time unit value, either as seconds (float) or string representation according to the mapping above.  
        years: the time unit years component.
        weeks: the time unit weeks component.
        months: the time unit weeks component.
        days: the time unit days component.
        hours: the time unit hours component.
        minutes: the time unit minutes component.
        seconds: the time unit seconds component.
        microseconds: the time unit microseconds component.
        trustme: a boolean switch to skip checks.
    """

    _CALENDAR = 'Calendar'
    _PHYSICAL = 'Physical'

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
                       'u': 'microseconds'
                      }

    def __init__(self, value=None, years=0, weeks=0, months=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0, trustme=False):

        if not trustme:

            if value:
                if is_numerical(value):
                    string = '{}s'.format(value)
                else:
                    if not isinstance(value, str):
                        raise TypeError('TimeUnits must be initialized with a number, a string or explicitly setting years, months, days, hours etc. (Got "{}")'.format(string.__class__.__name__))
                    string = value
            else:
                string = None

            # Value OR explicit time components
            if value and (years or months or days or hours or minutes or seconds or microseconds):
                raise ValueError('Choose between string/numerical init and explicit setting of years, months, days, hours etc.')

            # Check types:
            if not isinstance(years, int): raise ValueError('year not of type int (got "{}")'.format(years.__class__.__name__))
            if not isinstance(weeks, int): raise ValueError('weeks not of type int (got "{}")'.format(weeks.__class__.__name__))
            if not isinstance(months, int): raise ValueError('months not of type int (got "{}")'.format(months.__class__.__name__))
            if not isinstance(days, int): raise ValueError('days not of type int (got "{}")'.format(days.__class__.__name__))
            if not isinstance(hours, int): raise ValueError('hours not of type int (got "{}")'.format(hours.__class__.__name__))
            if not isinstance(minutes, int): raise ValueError('minutes not of type int (got "{}")'.format(minutes.__class__.__name__))
            if not isinstance(seconds, int): raise ValueError('seconds not of type int (got "{}")'.format(seconds.__class__.__name__))
            if not isinstance(microseconds, int): raise ValueError('microseconds not of type int (got "{}")'.format(microseconds.__class__.__name__))

        # Set the time components if given
        # TODO: set them only if given?
        self.years        = years
        self.months       = months
        self.weeks        = weeks
        self.days         = days
        self.hours        = hours
        self.minutes      = minutes 
        self.seconds      = seconds
        self.microseconds = microseconds

        if string:

            # Specific case for floating point seconds (TODO: improve me, maybe inlclude it in the regex?)
            if string.endswith('s') and '.' in string:
                if '_' in string:
                    raise NotImplementedError('Composite TimeUnits with floating point seconds not yet implemented.')
                self.seconds = int(string.split('.')[0])

                # Get decimal seconds as string 
                decimal_seconds_str = string.split('.')[1][0:-1] # Remove the last "s"

                # Ensure we can handle precision
                if len(decimal_seconds_str) > 6:
                    decimal_seconds_str = decimal_seconds_str[0:6]
                    #raise ValueError('Sorry, "{}" has too many decimal seconds to be handled with a TimeUnit (which supports up to the microsecond).'.format(string))

                # Add missing trailing zeros
                missing_trailing_zeros = 6-len(decimal_seconds_str)
                for _ in range(missing_trailing_zeros):
                    decimal_seconds_str += '0'

                # Cast to int & set
                self.microseconds = int(decimal_seconds_str)

            else:

                # Parse string using regex
                self.strings = string.split("_")
                regex = re.compile('^([0-9]+)([YMDWhmsu]{1,2})$')

                for string in self.strings:
                    try:
                        groups = regex.match(string).groups()
                    except AttributeError:
                        raise ValueError('Cannot parse string representation for the TimeUnit, unknown format ("{}")'.format(string)) from None

                    setattr(self, self._mapping_table[groups[1]], int(groups[0]))

        if not trustme:

            # If nothing set, raise error
            if not self.years and not self.weeks and not self.months and not self.days and not self.hours and not self.minutes and not self.seconds and not self.microseconds:
                raise ValueError('Detected zero-duration TimeUnit!')

    @property
    def value(self):
        """The value of the TimeUnit, as its string representation."""
        return(str(self))

    def __repr__(self):
        string = ''
        if self.years: string += str(self.years)               + 'Y' + '_'
        if self.months: string += str(self.months)             + 'M' + '_'
        if self.weeks: string += str(self.weeks)               + 'W' + '_'
        if self.days: string += str(self.days)                 + 'D' + '_'
        if self.hours: string += str(self.hours)               + 'h' + '_'
        if self.minutes: string += str(self.minutes)           + 'm' + '_'
        if self.seconds: string += str(self.seconds)           + 's' + '_'
        if self.microseconds: string += str(self.microseconds) + 'u' + '_'

        string = string[:-1]
        return string

    def __add__(self, other):

        if isinstance(other, self.__class__):  
            return TimeUnit(years        = self.years + other.years,
                            months       = self.months + other.months,
                            weeks        = self.weeks + other.weeks,
                            days         = self.days + other.days,
                            hours        = self.hours + other.hours,
                            minutes      = self.minutes + other.minutes,
                            seconds      = self.seconds + other.seconds,
                            microseconds = self.microseconds + other.microseconds)

        elif isinstance(other, datetime):
            if not other.tzinfo:
                raise ValueError('Timezone of the datetime to sum with is required')
            return self.shift(other, times=1)

        elif isinstance(other, Time):
            return Time(self.shift(other.dt(), times=1))

        elif is_numerical(other):
            return other + self.as_seconds()

        else:
            raise NotImplementedError('Adding TimeUnits with objects of class "{}" is not implemented'.format(other.__class__.__name__))

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):

        if isinstance(other, self.__class__):
            raise NotImplementedError('Subracting a TimeUnit from another TimeUnit is not implemented to prevent negative TimeUnits.')

        elif isinstance(other, datetime):
            if not other.tzinfo:
                raise ValueError('Timezone of the datetime to sum with is required')
            return self.shift(other, times=-1)

        elif isinstance(other, Time):
            return Time(self.shift(other.dt(), times=-1))

        elif is_numerical(other):
            return other - self.as_seconds()

        else:
            raise NotImplementedError('Subracting TimeUnits with objects of class "{}" is not implemented'.format(other.__class__.__name__))

    def __sub__(self, other):
        raise NotImplementedError('Cannot subtract anything from a TimeUnit. Only a TimeUnit from something else.')

    def __truediv__(self, other):
        raise NotImplementedError('Division for TimeUnits is not implemented')

    def __rtruediv__(self, other):
        raise NotImplementedError('Division for TimeUnits is not implemented')

    def __mul__(self, other):
        raise NotImplementedError('Multiplication for TimeUnits is not implemented')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):

        # Check against another TimeUnit
        if isinstance(other, TimeUnit):
            if self.is_calendar() and other.is_calendar():
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
                if self.microseconds != other.microseconds:
                    return False
                return True
            elif self.is_calendar() and not other.is_calendar():
                return False
            elif not self.is_calendar() and other.is_calendar():
                return False
            else:
                # Check using the duration in seconds, as 15m and 900s are actually the same unit
                if self.as_seconds() == other.as_seconds():
                    return True

        # Check for direct equality with value, i.e. comparing with a string
        if self.value == other:
            return True

        # Check for equality on the same "registered" value
        if isinstance(other, TimeUnit):
            if self.value == other.value:
                return True

        # Check for duration as seconds equality, i.e. comparing with a float
        try:
            if self.as_seconds() == other:
                return True
        except (TypeError, ValueError):
            # Raised if this or the other other TimeUnit is of calendar type, e.g.
            # ValueError: You can ask to get a calendar TimeUnit as seconds only if you provide the unit starting point
            pass

        # If everything fails, return false:
        return False

    def _is_composite(self):
        types = 0
        for item in self._mapping_table:
            if getattr(self, self._mapping_table[item]): types +=1
        return True if types > 1 else False 

    @property
    def type(self):
        """The type of the TimeUnit.

           - "Physical" if based on hours, minutes, seconds and  microseconds, which have fixed duration.
           - "Calendar" if based on years, months, weeks and days, which have variable duration depending on the starting date,
             and their math is not always well defined (e.g. adding a month to the 30th of January does not make sense)."""

        if self.years or self.months or self.weeks or self.days:
            return self._CALENDAR
        elif self.hours or self.minutes or self.seconds or self.microseconds:
            return self._PHYSICAL
        else:
            raise ConsistencyError('Error, TimeSlot not initialized?!')

    def is_physical(self):
        """Return True if the TimeUnit type is physical, False otherwise."""
        if self.type == self._PHYSICAL:
            return True
        else:
            return False

    def is_calendar(self):
        """Return True if the TimeUnit type is calendar, False otherwise."""
        if self.type == self._CALENDAR:
            return True 
        else:
            return False

    def round(self, time, how=None):
        """Round a Time or datetime according to this TimeUnit."""

        if self._is_composite():
            raise ValueError('Sorry, only simple TimeUnits are supported by the round operation')

        if isinstance(time, Time):
            time_dt = time.dt()
        else:
            time_dt = time

        if not time_dt.tzinfo:
            raise ValueError('The timezone of the Time or datetime is required')

        # Handle physical time 
        if self.type == self._PHYSICAL:

            # Convert input time to seconds
            time_s = s_from_dt(time_dt)
            tz_offset_s = get_tz_offset(time_dt)

            # Get TimeUnit duration in seconds
            time_unit_s = self.as_seconds(time_dt)

            # Apply modular math (including timezone time translation trick if required (multiple hours))
            # TODO: check for correctness, the time shift should be always done...

            if self.hours > 1 or self.minutes > 60:
                time_floor_s = ( (time_s - tz_offset_s) - ( (time_s - tz_offset_s) % time_unit_s) ) + tz_offset_s
            else:
                time_floor_s = time_s - (time_s % time_unit_s)

            time_ceil_s   = time_floor_s + time_unit_s

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

        # Handle calendar time 
        elif self.type == self._CALENDAR:

            if self.years:
                if self.years > 1:
                    raise NotImplementedError('Cannot round based on calendar TimeUnits with years > 1')
                floored_dt=time_dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            if self.months:
                if self.months > 1:
                    raise NotImplementedError('Cannot round based on calendar TimeUnits with months > 1')
                floored_dt=time_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if self.weeks:
                # Get to this day midnight
                floored_dt = TimeUnit('1D').floor(time_dt)

                # If not monday, subtract enought days to get there
                if floored_dt.weekday() != 0:
                    floored_dt = floored_dt - timedelta(days=floored_dt.weekday())

            if self.days:
                if self.days > 1:
                    raise NotImplementedError('Cannot round based on calendar TimeUnits with days > 1')
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

            else:
                ceiled_dt = self.shift(floored_dt, 1)
                distance_from_time_floor_s = abs(s_from_dt(time_dt) - s_from_dt(floored_dt)) # Distance from floor
                distance_from_time_ceil_s  = abs(s_from_dt(time_dt) - s_from_dt(ceiled_dt))  # Distance from ceil

                if distance_from_time_floor_s <= distance_from_time_ceil_s:
                    rounded_dt = floored_dt
                else:
                    rounded_dt = ceiled_dt

        # Handle other cases (Consistency error)
        else:
            raise ConsistencyError('Error, TimeUnit type not Physical nor Calendar?!')

        # Return
        if isinstance(time, Time):
            return Time(rounded_dt)
        else:
            return rounded_dt

    def floor(self, time):
        """Floor a Time or datetime according to this TimeUnit."""
        return self.round(time, how='floor')

    def ceil(self, time):
        """Ceil a Time or datetime according to this TimeUnit."""
        return self.round(time, how='ceil')

    def shift(self, time, times=1):
        """Shift a given Time or datetime n times this TimeUnit."""
        if self._is_composite():
            raise ValueError('Sorry, only simple TimeUnits are supported by the shift operation')
 
        if isinstance(time, Time):
            time_dt = time.dt()
        else:
            time_dt = time
 
        # Convert input time to seconds
        time_s = s_from_dt(time_dt)

        # Handle physical time TimeSlot
        if self.type == self._PHYSICAL:

            # Get TimeUnit duration in seconds
            time_unit_s = self.as_seconds()

            time_shifted_s = time_s + ( time_unit_s * times )
            time_shifted_dt = dt_from_s(time_shifted_s, tz=time_dt.tzinfo)

            return time_shifted_dt

        # Handle calendar time TimeSlot
        elif self.type == self._CALENDAR:

            if times != 1:
                raise NotImplementedError('Cannot shift calendar TimeUnits for times greater than 1 (got times="{}")'.format(times))

            # Create a TimeDelta object for everything but years and months
            delta = timedelta(weeks = self.weeks,
                              days = self.days,
                              hours = self.hours,
                              minutes = self.minutes,
                              seconds = self.seconds,
                              microseconds = self.microseconds)

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
                    # probably by adding a calendar time unit to a previous datetime
                    raise ValueError('Cannot shift "{}" by "{}" ({})'.format(time_dt,self,e)) from None

            # Check if we ended up on an ambiguous time
            if is_dt_ambiguous_without_offset(time_shifted_dt):
                time_shifted_dt_naive =  time_shifted_dt.replace(tzinfo=None)
                raise ValueError('Cannot shift "{}" by "{}" (Would end up on time {} which is ambiguous on time zone {})'.format(time_dt,self,time_shifted_dt_naive, time_shifted_dt.tzinfo)) from None

        # Handle other cases (Consistency error)
        else:
            raise ConsistencyError('Consistency error: TimeSlot type not physical nor calendar?!')

        # Return
        if isinstance(time, Time):
            return Time(time_shifted_dt)
        else:
            return time_shifted_dt

    def as_seconds(self, start=None):
        """The duration of the TimeUnit in seconds."""

        if start and isinstance(start, Time):
            start = start.dt()

        if self.type == self._CALENDAR:

            if not start:
                raise ValueError('You can ask to get a calendar TimeUnit as seconds only if you provide the unit starting point')

            if self._is_composite():
                raise ValueError('Sorry, only simple TimeUnits are supported by this operation')

            # Start Epoch
            start_epoch = s_from_dt(start)

            # End epoch
            end_dt = self.shift(start, 1)
            end_epoch = s_from_dt(end_dt)

            # Get duration based on seconds
            time_unit_s = end_epoch - start_epoch

        elif self.type == 'Physical':
            time_unit_s = 0
            if self.hours:
                time_unit_s += self.hours * 60 * 60
            if self.minutes:
                time_unit_s += self.minutes * 60
            if self.seconds:
                time_unit_s += self.seconds
            if self.microseconds:
                time_unit_s += 1/1000000.0 * self.microseconds

        else:
            raise ConsistencyError('Unknown TimeUnit type "{}"'.format(self.type))

        return float(time_unit_s)

