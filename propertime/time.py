# -*- coding: utf-8 -*-
"""Time classes"""

import pytz
from dateutil.tz.tz import tzoffset
from .utils import timezonize, dt_from_s, s_from_dt, dt_from_str, now_s, str_from_dt

# Setup logging
import logging
logger = logging.getLogger(__name__)


class Time(float):

    def __new__(cls, value=None, *args, **kwargs):
        
        from_seconds = False
        from_string = False
        
        # Handle value
        if isinstance(value, str):
            value = s_from_dt(dt_from_str(value))
            from_string = True
        
        elif value is None:
            value = now_s()
            from_seconds = True
            
        else:
            from_seconds = True

        # Create the new instance
        time_instance = super().__new__(cls, value)
        
        # Handle time zone & offset
        tz = kwargs.get('tz', None)
        offset = kwargs.get('offset', None)
        
        if tz:
            time_instance._tz = timezonize(tz)
            if from_seconds:  
                _dt = dt_from_s(value, tz=time_instance._tz)
                sign = -1 if _dt.utcoffset().days < 0 else 1 
                time_instance._offset = sign * _dt.utcoffset().seconds
            elif from_string:
                _dt = dt_from_s(value, tz=time_instance._tz)
                sign = -1 if _dt.utcoffset().days < 0 else 1 
                time_instance._offset = sign * _dt.utcoffset().seconds                
                
        elif offset:
            if from_string:
                raise ValueError('Cannot manually set an offset if initializing time from a string. Use the ISO notation.')
            time_instance._offset = offset
            time_instance._tz = None
        else:
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

