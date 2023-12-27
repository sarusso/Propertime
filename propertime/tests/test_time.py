# -*- coding: utf-8 -*-

import unittest
import pytz
from datetime import datetime
from ..utils import dt, correct_dt_dst, str_from_dt, dt_from_str, s_from_dt, dt_from_s, as_tz, timezonize, now_s
from ..time import Time
from dateutil.tz.tz import tzoffset

# Setup logging
from .. import logger
logger.setup()


class TestTime(unittest.TestCase):

    def test_init(self):

        # Now's time 
        time = Time()
        self.assertAlmostEqual(time, now_s(), delta=5)
        self.assertEqual(time.tz, pytz.UTC)
        self.assertEqual(time.offset, 0)

        # Now's time with time zone
        time = Time(offset=7200)
        self.assertEqual(time.offset, 7200)

        # Now's time with offset
        time = Time(tz='Europe/Rome')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time
        time = Time(5.6)
        self.assertEqual(time, 5.6)

        # Time with offset
        time = Time(1702928535.0, offset=7200)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 7200)

        time = Time(1702928535.0, offset=-68400)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, -68400)        

        # Time with time zone
        time = Time(1702928535.0, tz='America/New_York')
        self.assertEqual(str(time.tz), 'America/New_York')
        self.assertEqual(time.offset, -68400)        

        time = Time(1702928535.0, tz='Europe/Rome')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 3600)      

        # Time from naive datetime (assumed as UTC)
        time = Time(dt(2023,12,3,16,12,0))
        self.assertEqual(time, 1701619920.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')

        # Time from naive datetime with time zone as argument
        # Expected behavior: treat as on the given time zone
        time = Time(datetime(2023,12,3,16,12,0), tz='Europe/Rome')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time from naive datetime with offset as argument
        # Expected behavior: treat as with the given offset
        time = Time(datetime(2023,12,3,16,12,0), offset=3600)
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)
        
        # Time from datetime with offset
        time = Time(datetime(2023,12,3,16,12,0, tzinfo=tzoffset(None, 3600)))
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from datetime with UTC time zone
        time = Time(timezonize('UTC').localize(datetime(2023,12,3,16,12,0)))
        self.assertEqual(time, 1701619920.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+00:00')
        self.assertEqual(time.tz, pytz.UTC)
        
        # Time from datetime with time zone
        time = Time(timezonize('Europe/Rome').localize(datetime(2023,12,3,16,12,0)))
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time from datetime with offset and extra time zone
        # Expected behavior: move to the given time zone
        time = Time(datetime(2023,12,3,16,12,0, tzinfo=tzoffset(None, 3600)), tz='America/New_York')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 10:12:00-05:00')
        self.assertEqual(str(time.tz), 'America/New_York')

        # Time from datetime with time zone and extra time zone
        # Expected behavior: move to the given time zone
        time = Time(timezonize('Europe/Rome').localize(datetime(2023,12,3,16,12,0)), tz='America/New_York')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 10:12:00-05:00')
        self.assertEqual(str(time.tz), 'America/New_York')

        # Time from datetime with time zone and extra offset
        # Expected behavior: move to the given offset, discard original time zone
        time = Time(timezonize('America/New_York').localize(datetime(2023,12,3,10,12,0)), offset=3600)
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from naive string (assumed as UTC)
        time = Time('1986-08-01T16:46:00')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        # Time from string with a string on Zulu time
        time = Time('1986-08-01T16:46:00Z')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)
        
        # Time from string with an offset on UTC
        time = Time('1986-08-01T16:46:00+00:00')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        # Time from string with a different offset
        time = Time('1986-08-01T16:46:00+02:00')
        self.assertEqual(time, 523291560.0)
        self.assertEqual(str(time.tz), 'UTC')

        # Time from naive string with time zone as argument
        # Expected behavior: treat as on the given time zone
        time = Time('2023-12-03T16:12:00', tz='Europe/Rome')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time from naive datetime with offset as argument
        # Expected behavior: treat as with the given offset
        time = Time('2023-12-03T16:12:00', offset=3600)
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from string with an offset and an extra time zone
        time = Time('1986-08-01T16:46:00+02:00', tz='Europe/Rome')
        self.assertEqual(time, 523291560.0)
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # Time from string with an offset and an extra (different) time zone 
        time = Time('1986-08-01T16:46:00+02:00', tz='America/New_York')
        self.assertEqual(time, 523291560.0)
        self.assertEqual(str(time.tz), 'America/New_York')
        self.assertEqual(time.offset, -72000)


    def test_string_representation(self):
        
        # UTC
        time = Time(523291560)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 14:46:00 UTC)')

        # UTC sub-second
        time = Time(523291560.8377)
        self.assertEqual(str(time), 'Time: 523291560.8377 (1986-08-01 14:46:00.8377 UTC)')

        # Offset
        time = Time(523291560, offset=3600)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')

        # Offset non-hourly and sub-second
        time = Time(523291560, offset=3546.0945)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:45:06 +00:59:06.094500)')
                
        # Time zone
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome)')

    
    def test_conversions(self):
        
        # As datetime, on UTC
        time = Time(5.6)        
        self.assertEqual(time.dt(), datetime(1970,1,1,0,0,5,600000, tzinfo=pytz.UTC))
        
        # As datetime, with an offset
        time = Time(523291560, offset=1234)
        self.assertEqual(time.dt(), datetime(1986,8,1,15,6,34, tzinfo=tzoffset(None, 1234)))
              
        # As datetime, on Europe/Rome
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(time.dt(), dt(1986,8,1,16,46,0, tz='Europe/Rome'))
        
        # As ISO
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(time.iso(), '1986-08-01T16:46:00+02:00')


    def test_change_offset_and_timezone(self):
        
        # Change time zone
        time = Time(523291560, tz='Europe/Rome')
        time.dt() # Call it to trigger caching the _dt
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome)')
        self.assertEqual(time.offset, 7200)
        time.tz = 'America/New_York'
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 10:46:00 America/New_York)')
        self.assertEqual(time.offset, -72000)

        # Change offset
        time = Time(523291560, offset=3600)
        time.dt() # Call it to trigger caching the _dt
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')
        time.offset = 7200
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 +02:00)')

        # Also check that setting an offset after a time zone nullifies the time zone
        time = Time(523291560, tz='Europe/Rome')
        time.dt() # Call it to trigger caching the _dt
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome)')
        time.offset = 3600
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')
        self.assertEqual(time.tz, None)


    def test_operations(self):
  
        # Operations
        time1 = Time(4.3)
        time2 = Time(4.2)
        self.assertEqual(time1 + time2, 8.5)

