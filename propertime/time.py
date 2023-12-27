# -*- coding: utf-8 -*-
"""Time classes"""

import pytz
from datetime import datetime
from dateutil.tz.tz import tzoffset
from .utils import timezonize, dt_from_s, s_from_dt, dt_from_str, now_s, str_from_dt

# Setup logging
import logging
logger = logging.getLogger(__name__)


class Time(float):

    def __new__(cls, value=None, *args, **kwargs):

        embedded_tz = None
        embedded_offset = None

        # Handle value as datetime
        if isinstance(value, datetime):

            # Handle naive datetime if it is the case
            if not value.tzinfo:

                # Look at the tz argument if any, and decorate
                if kwargs.get('tz', None):
                    value = timezonize(kwargs.get('tz')).localize(value)

                # Look at the offset argument if any, and decorate
                elif kwargs.get('offset', None):
                    value = pytz.UTC.localize(value).replace(tzinfo = tzoffset(None, kwargs.get('offset')))

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
            if not (value[-1] == 'Z' or '+' in value or '-' in value.split('T')[1]):

                # Look at the tz argument if any, and use it
                if kwargs.get('tz', None):    
                    converted_dt = dt_from_str(value, tz=timezonize(kwargs.get('tz')))

                # Look at the offset argument if any, and use it
                elif kwargs.get('offset', None):
                    converted_dt = dt_from_str(value, tz=tzoffset(None, kwargs.get('offset')))

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
            # TODO: check float-compatible value type?
            #try:
            #    float(value)
            #except:
            #    raise ValueError('Cannot convert to float')
            pass

        # Create the new instance
        time_instance = super().__new__(cls, value)
        
        # Handle time zone & offset arguments. Can override "value" (string/datetime) ones.
        given_tz = timezonize(kwargs.get('tz', None))
        given_offset = kwargs.get('offset', None)

        if given_tz or (embedded_tz is not None and given_offset is None):

            # Set time zone, and also the offset
            tz = given_tz if given_tz else embedded_tz
            time_instance._tz = timezonize(tz)
            _dt = dt_from_s(value, tz=time_instance._tz)
            sign = -1 if _dt.utcoffset().days < 0 else 1 
            time_instance._offset = sign * _dt.utcoffset().seconds

        elif given_offset is not None or (embedded_offset is not None and not given_tz):

            # Set only the offset
            offset = given_offset if given_offset else embedded_offset
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
            dt_str = str(self.dt())
            if '+' in dt_str:
                tz_or_offset = '+'+dt_str.split('+')[1]
            else:
                tz_or_offset = '-'+dt_str.split('-')[1]
                
        
        if decimal_part == '0':
            return ('Time: {} ({} {})'.format(self_as_float, self.dt().strftime('%Y-%m-%d %H:%M:%S'), tz_or_offset))
        else:
            return ('Time: {} ({}.{} {})'.format(self_as_float, self.dt().strftime('%Y-%m-%d %H:%M:%S'), decimal_part, tz_or_offset))

    def __repr__(self):
        return self.__str__()
