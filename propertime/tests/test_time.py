# -*- coding: utf-8 -*-

import sys
import unittest
import pytz
from datetime import datetime
from ..utils import dt, correct_dt_dst, str_from_dt, dt_from_str, s_from_dt, dt_from_s, as_tz, timezonize, now_s
from ..time import Time, TimeSpan
from dateutil.tz.tz import tzoffset
try:
    from zoneinfo import ZoneInfo
except:
    print('WARNING: Will skip sub-second offsets tests as not supported until Python 3.9')
    ZoneInfo = None
if not(sys.version_info[0] >= 3 and sys.version_info[1] >= 7):
    print('WARNING: Will skip sub-second offsets tests as not supported until Python 3.7')

# Setup logging
from .. import logger
logger.setup()


class TestTime(unittest.TestCase):

    def test_init(self):

        # Now's time (UTC by default) 
        time = Time()
        self.assertAlmostEqual(time, now_s(), delta=5)
        self.assertEqual(time.tz, pytz.UTC)
        self.assertEqual(time.offset, 0)

        # Now's time (UTC by default) with explicit time zone
        time = Time(tz='UTC')
        self.assertEqual(time.tz, pytz.UTC)
        self.assertEqual(time.offset, 0)

        # Now's time (UTC by default) with explicit offset
        time = Time(offset=0)
        self.assertEqual(time.offset, 0)

        # Now's time (UTC by default) with inconsistent explicit offset
        with self.assertRaises(ValueError):
            Time(offset=3600)

        # Now's time (no time zone) with explicit offset
        time = Time(tz=None, offset=3600)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 3600)

        # Now's time with time zone
        time = Time(tz='Europe/Rome')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Now's time with time zone and explicit offset
        time = Time(tz='Europe/Rome', offset=3600)
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time (UTC by default)
        time = Time(5.6)
        self.assertEqual(time, 5.6)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        # Time (UTC by default) with explicit offset
        time = Time(1702928535.0, offset=0)
        self.assertEqual(time, 1702928535)
        self.assertEqual(time.tz, pytz.UTC)
        self.assertEqual(time.offset, 0)

        # Time (UTC by default) with inconsistent explicit offset
        with self.assertRaises(ValueError):
            Time(1702928535.0, offset=3500)

        # Time (no time zone) with explicit offset
        time = Time(1702928535.0, tz=None, offset=7200)
        self.assertEqual(time, 1702928535)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 7200)

        time = Time(1702928535.0, tz=None, offset=-68400)
        self.assertEqual(time, 1702928535)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, -68400)

        # Time with time zone
        time = Time(1702928535.0, tz='America/New_York')
        self.assertEqual(time, 1702928535)
        self.assertEqual(str(time.tz), 'America/New_York')
        self.assertEqual(time.offset, -18000)

        time = Time(1702928535.0, tz='Europe/Rome')
        self.assertEqual(time, 1702928535)
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 3600)

        time = Time(1702928535.0, tz=pytz.timezone('Europe/Rome'))
        self.assertEqual(time, 1702928535)
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 3600)

        if ZoneInfo:
            time = Time(1702928535.0, tz=ZoneInfo('Europe/Rome'))
            self.assertEqual(time, 1702928535)
            self.assertEqual(str(time.tz), 'Europe/Rome')
            self.assertEqual(time.offset, 3600)

        # Test from Time string representation
        time = Time(1650196535.0)
        time_from_str = Time(str(time))
        self.assertEqual(time, time_from_str)

        time = Time(1650196535.0, tz=None, offset=3600)
        time = Time(str(time))
        self.assertEqual(time, time_from_str)

        time = Time(1650196535.0, tz=None, offset=-18000)
        time = Time(str(time))
        self.assertEqual(time, time_from_str)

        time = Time(1650196535.0, tz='Europe/Rome')
        time = Time(str(time))
        self.assertEqual(time, time_from_str)

        with self.assertRaises(ValueError):
            Time('Time: 2818 (2023-10-29 02:15:00 Europe/Rome DST)')

        with self.assertRaises(ValueError):
            Time('Time: 1698538500.0 (2025-10-29 02:15:00 Europe/Rome DST)')

        # Time with datetime-like arguments
        time = Time(2023,12,1,0,0,0)
        self.assertEqual(time, 1701388800.0)
        self.assertEqual(str(time.to_dt()), '2023-12-01 00:00:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')

        # Time with datetime-like arguments and time zone as argument
        time = Time(2023,12,1,0,0,0, tz='Europe/Rome')
        self.assertEqual(time, 1701385200.0)
        self.assertEqual(str(time.to_dt()), '2023-12-01 00:00:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        time = Time(2023,12,1,0,0,0, tz=pytz.timezone('Europe/Rome'))
        self.assertEqual(time, 1701385200)
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 3600)

        if ZoneInfo:
            time = Time(2023,12,1,0,0,0, tz=ZoneInfo('Europe/Rome'))
            self.assertEqual(time, 1701385200)
            self.assertEqual(str(time.tz), 'Europe/Rome')
            self.assertEqual(time.offset, 3600)

        # Time with datetime-like arguments and offset as argument
        time = Time(2023,12,1,0,0,0, tz=None, offset=3600)
        self.assertEqual(time, 1701385200.0)
        self.assertEqual(str(time.to_dt()), '2023-12-01 00:00:00+01:00')
        self.assertEqual(time.tz, None)

        # Time with datetime-like arguments with both time zone and offset as arguments
        time = Time(2023, 6, 11, 17, 56, 0, offset=0, tz='UTC')
        self.assertEqual(str(time.to_dt()), '2023-06-11 17:56:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        time = Time(2023, 6, 11, 17, 56, 0, offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time.to_dt()), '2023-06-11 17:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # Time with datetime-like arguments and sub-second precision
        time = Time(2023,12,1,0,0,0.89)
        self.assertEqual(time, 1701388800.89)
        self.assertEqual(str(time.to_dt()), '2023-12-01 00:00:00.890000+00:00')
        self.assertEqual(str(time.tz), 'UTC')

        # Inconsistent time zone - offset combination
        with self.assertRaises(ValueError):
            Time(2023, 6, 11, 17, 56, 0, offset=3600, tz='Europe/Rome') 

        with self.assertRaises(ValueError):
            Time(2023, 6, 11, 17, 56, 0, offset=10800, tz='Europe/Rome')

        # Invalid init string
        with self.assertRaises(ValueError):
            Time('aaa')

        # Unknown init type
        with self.assertRaises(ValueError):
            Time({})

        # Not existent time
        with self.assertRaises(ValueError):
            Time(2023,3,26,2,15,0, tz='Europe/Rome')

        # Ambiguous time
        with self.assertRaises(ValueError):
            Time(2023,10,29,2,15,0, tz='Europe/Rome')

        # Ambiguous time with guessing enabled (just raises a warning)
        time = Time(2023,10,29,2,15,0, tz='Europe/Rome', guessing=True)
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')
        self.assertEqual(time.to_iso(), '2023-10-29T02:15:00+01:00')

        # Ambiguous time with offset OK
        time = Time(2023,10,29,2,15,0, offset=3600, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')
        self.assertEqual(time.to_iso(), '2023-10-29T02:15:00+01:00')

        time = Time(2023,10,29,2,15,0, offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698538500.0 (2023-10-29 02:15:00 Europe/Rome DST)')
        self.assertEqual(time.to_iso(), '2023-10-29T02:15:00+02:00')

        time = Time(2023,11,5,1,15,0, offset=-3600*4, tz='America/New_York')
        self.assertEqual(str(time), 'Time: 1699161300.0 (2023-11-05 01:15:00 America/New_York DST)')
        self.assertEqual(time.to_iso(), '2023-11-05T01:15:00-04:00')

        # Extra stuff for float interface compatibility
        self.assertEqual(Time.fromhex('0x1.ffffp10'), 2047.984375)
        self.assertIsInstance(Time.fromhex('0x1.ffffp10'), Time)
        self.assertEqual(Time(123).hex(), '0x1.ec00000000000p+6')
        self.assertTrue(Time(123).is_integer())
        self.assertTrue(Time(123.0).is_integer())
        self.assertFalse(Time(123.4).is_integer())

    def test_properties(self):

        time = Time(3600, offset=10, tz=None)
        self.assertEqual(time.offset, 10)
        self.assertIsInstance(time.offset, int)

        time = Time(3600, offset=10.0, tz=None)
        self.assertEqual(time.offset, 10.0)
        self.assertIsInstance(time.offset, float)

        time = Time(3600, tz=pytz.UTC)
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        time = Time(3600, tz='America/New_York')
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        time = Time(3600, tz=pytz.timezone('America/New_York'))
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        if ZoneInfo:
            time = Time(2023,12,3,10,12,0, tz=ZoneInfo('America/New_York'))
            self.assertIsInstance(time.tz, ZoneInfo)

        time = Time(2023,12,3,10,12,0)
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        time = Time(2023,12,3,10,12,0, tz=pytz.UTC)
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        time = Time(2023,12,3,10,12,0, tz='America/New_York')
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        time = Time(2023,12,3,10,12,0, tz=pytz.timezone('America/New_York'))
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)

        if ZoneInfo:
            time = Time(2023,12,3,10,12,0, tz=ZoneInfo('America/New_York'))
            self.assertIsInstance(time.tz, ZoneInfo)

        time = Time(3600)
        self.assertIsInstance(time.tz, pytz.BaseTzInfo)
        self.assertEqual(time.offset, 0)
        self.assertIsInstance(time.offset, int)


    def test_conversions(self):

        # Time from naive datetime not allowed
        with self.assertRaises(ValueError):
            Time.from_dt(datetime(2023,12,3,16,12,0))

        # Time from naive datetime with time zone as argument
        # Expected behavior: treat as if on the given time zone
        time = Time.from_dt(datetime(2023,12,3,16,12,0), tz='Europe/Rome')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time from naive datetime with offset as argument
        # Expected behavior: treat as if with the given offset
        time = Time.from_dt(datetime(2023,12,3,16,12,0), offset=3600)
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from datetime with offset
        time = Time.from_dt(datetime(2023,12,3,16,12,0, tzinfo=tzoffset(None, 3600)))
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from datetime with UTC time zone
        time = Time.from_dt(timezonize('UTC').localize(datetime(2023,12,3,16,12,0)))
        self.assertEqual(time, 1701619920.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+00:00')
        self.assertEqual(time.tz, pytz.UTC)

        # Time from datetime with time zone
        time = Time.from_dt(timezonize('Europe/Rome').localize(datetime(2023,12,3,16,12,0)))
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        if ZoneInfo:
            # Time from datetime with time zone with ZoneInfo
            time = Time.from_dt(datetime(2023,12,3,10,12,0, tzinfo=ZoneInfo('America/New_York')))
            self.assertEqual(time, 1701616320.0)
            self.assertEqual(str(time.to_dt()), '2023-12-03 10:12:00-05:00')
            self.assertEqual(str(time.tz), 'America/New_York')

        # Time from datetime with offset and extra time zone
        # Expected behavior: move to the given time zone
        time = Time.from_dt(datetime(2023,12,3,16,12,0, tzinfo=tzoffset(None, 3600)), tz='America/New_York')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 10:12:00-05:00')
        self.assertEqual(str(time.tz), 'America/New_York')

        # Time from datetime with time zone and extra time zone
        # Expected behavior: move to the given time zone
        time = Time.from_dt(timezonize('Europe/Rome').localize(datetime(2023,12,3,16,12,0)), tz='America/New_York')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 10:12:00-05:00')
        self.assertEqual(str(time.tz), 'America/New_York')

        # Time from datetime with time zone and extra offset
        # Expected behavior: move to the given offset, discard original time zone
        time = Time.from_dt(timezonize('America/New_York').localize(datetime(2023,12,3,10,12,0)), offset=3600)
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from datetime with an offset and both an extra offset and time zone as arguments
        # Expected behavior: move to the given time zone, check offset compatibility
        time = Time.from_dt(datetime(2023,6,11,17,56,0, tzinfo=pytz.UTC), offset=0, tz='UTC')
        self.assertEqual(str(time.to_dt()), '2023-06-11 17:56:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        time = Time.from_dt(datetime(2023,6,11,17,56,0, tzinfo=pytz.UTC), offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time.to_dt()), '2023-06-11 19:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # Inconsistent time zone - offset combination
        with self.assertRaises(ValueError):
            Time.from_dt(timezonize('America/New_York').localize(datetime(2023,12,3,10,12,0)), tz='Europe/Rome', offset=0)

        # Ambiguous time
        with self.assertRaises(ValueError):
            Time.from_dt(datetime(2023,10,29,2,15,0), tz='Europe/Rome')

        # This is not ambiguous for the from_dt method. It was for the .localize().
        time = Time.from_dt(timezonize('Europe/Rome').localize(datetime(2023,10,29,2,15,0)))

        # Ambiguous time with guessing enabled (just raises a warning)
        time = Time(2023,10,29,2,15,0, tz='Europe/Rome', guessing=True)
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')
        self.assertEqual(time.to_iso(), '2023-10-29T02:15:00+01:00')

        # Ambiguous time with offset OK
        time = Time(2023,10,29,2,15,0, offset=3600, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')
        self.assertEqual(time.to_iso(), '2023-10-29T02:15:00+01:00')

        time = Time(2023,10,29,2,15,0, offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698538500.0 (2023-10-29 02:15:00 Europe/Rome DST)')
        self.assertEqual(time.to_iso(), '2023-10-29T02:15:00+02:00')

        # Time from naive string not allowed
        with self.assertRaises(ValueError):
            Time.from_iso('1986-08-01T16:46:00')

        # Time from naive string with an extra (zero) offset
        # Expected behavior: treat as if with the given offset
        time = Time.from_iso('2023-06-11T17:56:00', offset=0)
        self.assertEqual(time, 1686506160.0)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 0)

        # Time from naive string with an extra offset
        # Expected behavior: treat as if with the given offset
        time = Time.from_iso('2023-06-11T17:56:00', offset=3600)
        self.assertEqual(time, 1686502560.0)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 3600)

        # Time from string with a string on Zulu time
        time = Time.from_iso('1986-08-01T16:46:00Z')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        # Time from string with an offset on UTC
        time = Time.from_iso('1986-08-01T16:46:00+00:00')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(time.offset, 0)
        self.assertEqual(time.tz, None)

        # Time from string with a different offset
        time = Time.from_iso('2023-12-25T16:12:00+01:00')
        self.assertEqual(time, 1703517120.0)
        self.assertEqual(time.offset, 3600)
        self.assertEqual(time.tz, None)

        # Time from naive string with time zone as argument
        # Expected behavior: treat as on the given time zone
        time = Time.from_iso('2023-12-03T16:12:00', tz='Europe/Rome')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time from naive datetime with offset as argument
        # Expected behavior: treat as with the given offset
        time = Time.from_iso('2023-12-03T16:12:00', offset=3600)
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.to_dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(time.tz, None)

        # Time from string with an offset and an extra time zone
        time = Time.from_iso('1986-08-01T16:46:00+02:00', tz='Europe/Rome')
        self.assertEqual(time, 523291560.0)
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # Time from string with an offset and an extra (different) time zone 
        time = Time.from_iso('1986-08-01T16:46:00+02:00', tz='America/New_York')
        self.assertEqual(time, 523291560.0)
        self.assertEqual(str(time.tz), 'America/New_York')
        self.assertEqual(time.offset, -14400)

        # Time from string with an offset and both an extra offset and time zone as arguments
        # Expected behavior: move to the given time zone, check offset compatibility
        time = Time.from_iso('2023-06-11T17:56:00+00:00', offset=0, tz='UTC')
        self.assertEqual(str(time.to_dt()), '2023-06-11 17:56:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        time = Time.from_iso('2023-06-11T17:56:00+00:00', offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time.to_dt()), '2023-06-11 19:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # Inconsistent time zone - offset combination
        with self.assertRaises(ValueError):
            Time.from_iso('2023-06-11T17:56:00+00:00', offset=0, tz='Europe/Rome') # 17:56 UTC

        with self.assertRaises(ValueError):
            Time.from_iso('2023-06-11T17:56:00+03:00', offset=10800, tz='Europe/Rome') # 14:56 UTC

        # Extra check for otherwise ambiguous time
        time = Time.from_iso('2023-10-29T02:15:00+01:00', tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')

        time = Time.from_iso('2023-10-29T02:15:00+02:00', tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698538500.0 (2023-10-29 02:15:00 Europe/Rome DST)')

        # To datetime, on UTC
        time = Time(5.6)
        self.assertEqual(time.to_dt(), datetime(1970,1,1,0,0,5,600000, tzinfo=pytz.UTC))

        # To datetime, with an offset
        time = Time(523291560, tz=None, offset=1234)
        self.assertEqual(time.to_dt(), datetime(1986,8,1,15,6,34, tzinfo=tzoffset(None, 1234)))

        # To datetime, with a sub-second offset
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
            time = Time(900, tz=None, offset=2.6)
            self.assertEqual(time.to_dt(), datetime(1970,1,1,0,15,2,600000, tzinfo=tzoffset(None, 2.6)))

        # To datetime, on Europe/Rome
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(time.to_dt(), dt(1986,8,1,16,46,0, tz='Europe/Rome'))

        # To ISO
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(time.to_iso(), '1986-08-01T16:46:00+02:00')


    def test_representations(self):

        # UTC
        time = Time(523291560)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 14:46:00 UTC)')

        # UTC sub-second
        time = Time(523291560.8377)
        self.assertEqual(str(time), 'Time: 523291560.8377 (1986-08-01 14:46:00.8377 UTC)')

        # Offset
        time = Time(523291560, tz=None, offset=3600)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')

        # Negative offset
        time = Time(1702928535.0, tz=None, offset=-68400)
        self.assertEqual(str(time), 'Time: 1702928535.0 (2023-12-18 00:42:15 -19:00)')

        # Offset non-hourly
        time = Time(523291560, tz=None,  offset=3546)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:45:06 +00:59:06)')

        # Offset sub-second
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
            time = Time(523291560, tz=None, offset=3546.0945)
            self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:45:06 +00:59:06.094500)')

        # Time zone
        time = Time(1702928535.0, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1702928535.0 (2023-12-18 20:42:15 Europe/Rome)')

        # Time zone plus DST
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')

        # Lastly test also repr
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(repr(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')


    def test_as_timezone_and_offset(self):

        # Get Time as another time zone
        time = Time(523291560, tz='Europe/Rome')
        time.to_dt() # Call it to trigger caching the _dt
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')
        self.assertEqual(time.offset, 7200)
        time = time.as_tz('America/New_York')
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 10:46:00 America/New_York DST)')
        self.assertEqual(time.offset, -72000)

        # Change offset
        time = Time(523291560, tz=None, offset=3600)
        time.to_dt() # Call it to trigger caching the _dt
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')
        time = time.as_offset(7200)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 +02:00)')

        # Also check that setting an offset after a time zone nullifies the time zone
        time = Time(523291560, tz='Europe/Rome')
        time.to_dt() # Call it to trigger caching the _dt
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')
        time = time.as_offset(3600)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')
        self.assertEqual(time.tz, None)


    def test_operations(self):

        time1 = Time(4.3)
        time2 = Time(4.2)
        dt1 = dt(1970,1,1,0,0,4,3, tz='UTC')
        dt2 = dt(1970,1,1,0,0,4,2, tz='UTC')

        # Operations with Time objects
        result = time1 + time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) + float(time2))

        result = time1 - time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) - float(time2))

        result = time1 * time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) * float(time2))

        result = time1 / time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) / float(time2))

        result = time1 % time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) % float(time2))

        result = time1 ** time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) ** float(time2))

        result = time1 // time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) // float(time2))

        # Operations with numerical values (normal)
        result = time1 + 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) + 10)

        result = time1 - 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) - 10)

        result = time1 * 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) * 10)

        result = time1 / 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) / 10)

        result = time1 % 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) % 10)

        result = time1 ** 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) ** 10)

        result = time1 // 10
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) // 10)

        # Operations with numerical values (right)
        result = 10 + time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 + float(time1))

        result = 10 - time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 - float(time1))

        result = 10 * time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 * float(time1))

        result = 10 / time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 / float(time1))

        result = 10 % time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 % float(time1))

        result = 10 ** time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 ** float(time1))

        result = 10 // time1
        self.assertIsInstance(result, Time)
        self.assertEqual(result, 10 // float(time1))


        # Operations with datetimes (normal)
        result = time1 + dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) + s_from_dt(dt2))

        result = time1 - dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) - s_from_dt(dt2))

        result = time1 * dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) * s_from_dt(dt2))

        result = time1 / dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) / s_from_dt(dt2))

        result = time1 % dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) % s_from_dt(dt2))

        result = time1 ** dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) ** s_from_dt(dt2))

        result = time1 // dt2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, float(time1) // s_from_dt(dt2))


        # Operations with datetimes (right)
        result = dt1 + time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) + float(time2))

        result = dt1 - time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) - float(time2))

        result = dt1 * time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) * float(time2))

        result = dt1 / time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) / float(time2))

        result = dt1 % time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) % float(time2))

        result = dt1 ** time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) ** float(time2))

        result = dt1 // time2
        self.assertIsInstance(result, Time)
        self.assertEqual(result, s_from_dt(dt1) // float(time2))


        # Some edge cases
        self.assertEqual(time1 + Time(1970,1,1,2,0,0, tz=None, offset=3600), 3604.3)
        self.assertEqual(Time(1970,1,1,2,0,0, tz=None, offset=3600) + time1, 3604.3)


        # Wrong combinations (only for the sum, as the underlying logic is the same). TODO: improve me?
        with self.assertRaises(ValueError):
            time1 + Time(1970,1,1,1,0,0, tz='Europe/Rome')

        with self.assertRaises(ValueError):
            Time(1970,1,1,1,0,0, tz='Europe/Rome') + time2

        with self.assertRaises(ValueError):
            time1 + dt(1970,1,1,1,0,0, tz='Europe/Rome')

        with self.assertRaises(ValueError):
            dt(1970,1,1,1,0,0, tz='Europe/Rome') + time2

        with self.assertRaises(ValueError):
            Time(1970,1,1,1,0,0, tz=None, offset=7200) + Time(1970,1,1,1,0,0, tz=None, offset=3600)

        with self.assertRaises(ValueError):
            time1 + dt(1970,1,1,1,0,0, naive=True)



class TestTimeSpans(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(ValueError):
            _ = TimeSpan('15m', '20s')

        # Not valid 'q' type
        with self.assertRaises(ValueError):
            _ = TimeSpan('15q')

        # Numerical init
        time_span_1 = TimeSpan(seconds=60)
        self.assertEqual(str(time_span_1), '60s')

        # String init
        time_span_1 = TimeSpan('15m')
        self.assertEqual(str(time_span_1), '15m')

        time_span_2 = TimeSpan('15m_30.3s')
        self.assertEqual(str(time_span_2), '15m_30.3s')

        # Components init
        self.assertEqual(TimeSpan(days=1).days, 1)
        self.assertEqual(TimeSpan(years=2).years, 2)
        self.assertEqual(TimeSpan(minutes=1).minutes, 1)
        self.assertEqual(TimeSpan(minutes=15).minutes, 15)
        self.assertEqual(TimeSpan(hours=1).hours, 1)

        # Test various init and correct handling of time componentes
        self.assertEqual(TimeSpan('1D').days, 1)
        self.assertEqual(TimeSpan('2Y').years, 2)
        self.assertEqual(TimeSpan('1m').minutes, 1)
        self.assertEqual(TimeSpan('15m').minutes, 15)
        self.assertEqual(TimeSpan('1h').hours, 1)

        # Test floating point seconds init
        self.assertEqual(TimeSpan('1.2345s').as_seconds(), 1.2345)
        self.assertEqual(TimeSpan('1.234s').as_seconds(), 1.234)
        self.assertEqual(TimeSpan('1.02s').as_seconds(), 1.02)
        self.assertEqual(TimeSpan('1.000005s').as_seconds(), 1.000005)
        self.assertEqual(TimeSpan('67.000005s').seconds, 67.000005)

        # Too much precision (below microseconds), raise an error
        with self.assertRaises(ValueError):
            TimeSpan('1.00000005s')

        # Test span simple equalities and inequalities
        self.assertEqual(TimeSpan(hours=1), TimeSpan(hours=1))
        self.assertEqual(TimeSpan(hours=1), '1h')
        self.assertNotEqual(TimeSpan(hours=1), TimeSpan(hours=2))
        self.assertNotEqual(TimeSpan(hours=1), 'a_string')

        self.assertEqual(TimeSpan(days=1), TimeSpan(days=1))
        self.assertEqual(TimeSpan(days=1), '1D')
        self.assertNotEqual(TimeSpan(days=1), TimeSpan(days=2))
        self.assertNotEqual(TimeSpan(days=1), 'a_string')

        # Test span composite equalities and inequalities
        self.assertEqual(TimeSpan('1h'), TimeSpan('3600s'))
        self.assertEqual(TimeSpan('1h'), TimeSpan(hours=1))

        self.assertNotEqual(TimeSpan('24h'), TimeSpan('1D'))
        self.assertNotEqual(TimeSpan('86400s'), TimeSpan('1D'))


    def test_representations(self):

        self.assertEqual(str(TimeSpan('600.0s')), '600s')

        self.assertEqual(str(TimeSpan(seconds=600)), '600s')
        self.assertEqual(str(TimeSpan(seconds=600.0)), '600s')
        self.assertEqual(str(TimeSpan(seconds=600.45)), '600.45s') 

        self.assertEqual(str(TimeSpan(days=1)), '1D')
        self.assertEqual(str(TimeSpan(years=2)), '2Y')
        self.assertEqual(str(TimeSpan(minutes=1)), '1m')
        self.assertEqual(str(TimeSpan(minutes=15)), '15m')
        self.assertEqual(str(TimeSpan(hours=1)), '1h')

        self.assertEqual(str(TimeSpan('15m')), '15m')
        self.assertEqual(str(TimeSpan('15m_30.3s')), '15m_30.3s')

        self.assertEqual(repr(TimeSpan(days=1)), '1D')



    def test_as_seconds(self):

        datetime1 = dt(2015,10,24,0,15,0, tz='Europe/Rome')
        datetime2 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime3 = dt(2015,10,26,0,15,0, tz='Europe/Rome')
 
        # Day span
        time_span = TimeSpan('1D')
        with self.assertRaises(ValueError):
            time_span.as_seconds()
        self.assertEqual(time_span.as_seconds(datetime1), 86400) # No DST, standard day
        self.assertEqual(time_span.as_seconds(datetime2), 90000) # DST, change

        # Week span
        time_span = TimeSpan('1W')
        with self.assertRaises(ValueError):
            time_span.as_seconds()
        self.assertEqual(time_span.as_seconds(datetime1), (86400*7)+3600)
        self.assertEqual(time_span.as_seconds(datetime3), (86400*7))

        # Month span
        time_span = TimeSpan('1M')
        with self.assertRaises(ValueError):
            time_span.as_seconds()
        self.assertEqual(time_span.as_seconds(datetime3), (86400*31)) # October has 31 days so next month same day has 31 full days
        self.assertEqual(time_span.as_seconds(datetime1), ((86400*31)+3600)) # Same as above, but in this case we have a DST change in the middle

        # Year span
        time_span = TimeSpan('1Y')
        with self.assertRaises(ValueError):
            time_span.as_seconds()
        self.assertEqual(time_span.as_seconds(dt(2014,10,24,0,15,0, tz='Europe/Rome')), (86400*365)) # Standard year
        self.assertEqual(time_span.as_seconds(dt(2015,10,24,0,15,0, tz='Europe/Rome')), (86400*366)) # Leap year

        # Test duration with composite seconds init
        self.assertEqual(TimeSpan(minutes=1, seconds=3).as_seconds(), 63)


    def test_shift(self):

        datetime1 = dt(2015,10,24,0,15,0, tz='Europe/Rome')
        datetime2 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime3 = dt(2015,10,26,0,15,0, tz='Europe/Rome')

        # Day span
        time_span = TimeSpan('1D')
        self.assertEqual(time_span.shift(datetime1), dt(2015,10,25,0,15,0, tz='Europe/Rome')) # No DST, standard day
        self.assertEqual(time_span.shift(datetime2), dt(2015,10,26,0,15,0, tz='Europe/Rome')) # DST, change

        # Day span on not-existent hour due to DST
        starting_dt = dt(2023,3,25,2,15, tz='Europe/Rome')
        with self.assertRaises(ValueError):
            starting_dt + TimeSpan('1D')

        # Day span on ambiguous hour due to DST
        starting_dt = dt(2023,10,28,2,15, tz='Europe/Rome')
        with self.assertRaises(ValueError):
            starting_dt + TimeSpan('1D')

        # Week span
        time_span = TimeSpan('1W')
        self.assertEqual(time_span.shift(datetime1), dt(2015,10,31,0,15,0, tz='Europe/Rome'))
        self.assertEqual(time_span.shift(datetime3), dt(2015,11,2,0,15,0, tz='Europe/Rome'))

        # Month span
        time_span = TimeSpan('1M')
        self.assertEqual(time_span.shift(datetime1), dt(2015,11,24,0,15,0, tz='Europe/Rome'))
        self.assertEqual(time_span.shift(datetime2), dt(2015,11,25,0,15,0, tz='Europe/Rome'))
        self.assertEqual(time_span.shift(datetime3), dt(2015,11,26,0,15,0, tz='Europe/Rome'))

        # Test 12%12 must give 12 edge case
        self.assertEqual(time_span.shift(dt(2015,1,1,0,0,0, tz='Europe/Rome')), dt(2015,2,1,0,0,0, tz='Europe/Rome'))
        self.assertEqual(time_span.shift(dt(2015,11,1,0,0,0, tz='Europe/Rome')), dt(2015,12,1,0,0,0, tz='Europe/Rome'))

        # Year span
        time_span = TimeSpan('1Y')
        self.assertEqual(time_span.shift(datetime1), dt(2016,10,24,0,15,0, tz='Europe/Rome'))


    def test_ceil_floor_round(self):

        # Test that complex time_spans are not handable
        time_span = TimeSpan('1D_3h_5m')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome')

        with self.assertRaises(ValueError):
            _ = time_span.floor(datetime)

        # Test in ceil/floor/round normal conditions (days)
        time_span = TimeSpan('1D')
        self.assertEqual(time_span.ceil(dt(2023,11,25,10,0,0, tz='Europe/Rome')), time_span.round(dt(2023,11,26,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.floor(dt(2023,11,25,19,0,0, tz='Europe/Rome')), time_span.round(dt(2023,11,25,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.round(dt(2023,11,25,10,0,0, tz='Europe/Rome')), time_span.round(dt(2023,11,25,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.round(dt(2023,11,25,12,0,0, tz='Europe/Rome')), time_span.round(dt(2023,11,25,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.round(dt(2023,11,25,13,0,0, tz='Europe/Rome')), time_span.round(dt(2023,11,26,0,0,0, tz='Europe/Rome')))

        # Test in ceil/floor/round across DST change (days)
        time_span = TimeSpan('1D')
        self.assertEqual(time_span.ceil(dt(2023,3,26,10,0,0, tz='Europe/Rome')), time_span.round(dt(2023,3,27,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.floor(dt(2023,3,26,19,0,0, tz='Europe/Rome')), time_span.round(dt(2023,3,26,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.round(dt(2023,3,26,12,30,0, tz='Europe/Rome')), time_span.round(dt(2023,3,26,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_span.round(dt(2023,3,26,12,31,0, tz='Europe/Rome')), time_span.round(dt(2023,3,27,0,0,0, tz='Europe/Rome')))

        # Test in ceil/floor/round normal conditions (hours)
        time_span = TimeSpan('1h')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome')
        self.assertEqual(time_span.floor(datetime), dt(2015,1,1,16,0,0, tz='Europe/Rome'))
        self.assertEqual(time_span.ceil(datetime), dt(2015,1,1,17,0,0, tz='Europe/Rome'))

        # Test in ceil/floor/round normal conditions (minutes)
        time_span = TimeSpan('15m')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome')
        self.assertEqual(time_span.floor(datetime), dt(2015,1,1,16,30,0, tz='Europe/Rome'))
        self.assertEqual(time_span.ceil(datetime), dt(2015,1,1,16,45,0, tz='Europe/Rome'))

        # Test ceil/floor/round in normal conditions (seconds)
        time_span = TimeSpan('30s')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome') 
        self.assertEqual(time_span.floor(datetime), dt(2015,1,1,16,37,0, tz='Europe/Rome'))
        self.assertEqual(time_span.ceil(datetime), dt(2015,1,1,16,37,30, tz='Europe/Rome'))

        # Test ceil/floor/round across 1970-1-1 (minutes) 
        time_span = TimeSpan('5m')
        datetime1 = dt(1969,12,31,23,57,29, tz='UTC') # epoch = -3601
        datetime2 = dt(1969,12,31,23,59,59, tz='UTC') # epoch = -3601
        self.assertEqual(time_span.floor(datetime1), dt(1969,12,31,23,55,0, tz='UTC'))
        self.assertEqual(time_span.ceil(datetime1), dt(1970,1,1,0,0, tz='UTC'))
        self.assertEqual(time_span.round(datetime1), dt(1969,12,31,23,55,0, tz='UTC'))
        self.assertEqual(time_span.round(datetime2), dt(1970,1,1,0,0, tz='UTC'))

        # Test ceil/floor/round (3 hours-test)
        time_span = TimeSpan('3h')
        datetime = dt(1969,12,31,23,0,1, tz='Europe/Rome') # negative epoch
        self.assertEqual(time_span.floor(datetime), dt(1969,12,31,23,0,0, tz='Europe/Rome'))
        self.assertEqual(time_span.ceil(datetime), dt(1970,1,1,2,0, tz='Europe/Rome'))

        # Test ceil/floor/round across 1970-1-1 (together with the 2 hours-test, TODO: decouple) 
        time_span = TimeSpan('2h')
        datetime1 = dt(1969,12,31,22,59,59, tz='Europe/Rome') # negative epoch
        datetime2 = dt(1969,12,31,23,0,1, tz='Europe/Rome') # negative epoch  
        self.assertEqual(time_span.floor(datetime1), dt(1969,12,31,22,0,0, tz='Europe/Rome'))
        self.assertEqual(time_span.ceil(datetime1), dt(1970,1,1,0,0, tz='Europe/Rome'))
        self.assertEqual(time_span.round(datetime1), dt(1969,12,31,22,0, tz='Europe/Rome'))
        self.assertEqual(time_span.round(datetime2), dt(1970,1,1,0,0, tz='Europe/Rome'))

        # Test ceil/floor/round across DST change (hours)
        time_span = TimeSpan('1h')

        datetime1 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime2 = datetime1 + time_span    # 2015-10-25 01:15:00+02:00
        datetime3 = datetime2 + time_span    # 2015-10-25 02:15:00+02:00
        datetime4 = datetime3 + time_span    # 2015-10-25 02:15:00+01:00

        datetime1_rounded = dt(2015,10,25,0,0,0, tz='Europe/Rome')
        datetime2_rounded = datetime1_rounded + time_span
        datetime3_rounded = datetime2_rounded + time_span
        datetime4_rounded = datetime3_rounded + time_span
        datetime5_rounded = datetime4_rounded + time_span

        self.assertEqual(time_span.floor(datetime2), datetime2_rounded)
        self.assertEqual(time_span.ceil(datetime2), datetime3_rounded)

        self.assertEqual(time_span.floor(datetime3), datetime3_rounded)
        self.assertEqual(time_span.ceil(datetime3), datetime4_rounded)

        self.assertEqual(time_span.floor(datetime4), datetime4_rounded)
        self.assertEqual(time_span.ceil(datetime4), datetime5_rounded)

        # Test ceil/floor/round with a calendar time span and across a DST change

        # Day span
        time_span = TimeSpan('1D')

        datetime1 = dt(2015,10,25,4,15,34, tz='Europe/Rome') # DST off (+01:00)
        datetime1_floor = dt(2015,10,25,0,0,0, tz='Europe/Rome') # DST on (+02:00)
        datetime1_ceil = dt(2015,10,26,0,0,0, tz='Europe/Rome') # DST off (+01:00)

        self.assertEqual(time_span.floor(datetime1), datetime1_floor)
        self.assertEqual(time_span.ceil(datetime1), datetime1_ceil)

        # Week span
        time_span = TimeSpan('1W')

        datetime1 = dt(2023,10,29,15,47, tz='Europe/Rome') # DST off (+01:00)
        datetime1_floor = dt(2023,10,23,0,0, tz='Europe/Rome') # DST on (+02:00)
        datetime1_ceil = dt(2023,10,30,0,0, tz='Europe/Rome') # DST off (+01:00)

        self.assertEqual(time_span.floor(datetime1), datetime1_floor)
        self.assertEqual(time_span.ceil(datetime1), datetime1_ceil)

        # Month span
        time_span = TimeSpan('1M')

        datetime1 = dt(2015,10,25,4,15,34, tz='Europe/Rome') # DST off (+01:00)
        datetime1_floor = dt(2015,10,1,0,0,0, tz='Europe/Rome') # DST on (+02:00)
        datetime1_ceil = dt(2015,11,1,0,0,0, tz='Europe/Rome') # DST off (+01:00)

        self.assertEqual(time_span.floor(datetime1), datetime1_floor)
        self.assertEqual(time_span.ceil(datetime1), datetime1_ceil)

        # Year span
        time_span = TimeSpan('1Y')

        datetime1 = dt(2015,10,25,4,15,34, tz='Europe/Rome')
        datetime1_floor = dt(2015,1,1,0,0,0, tz='Europe/Rome')
        datetime1_ceil = dt(2016,1,1,0,0,0, tz='Europe/Rome')

        self.assertEqual(time_span.floor(datetime1), datetime1_floor)
        self.assertEqual(time_span.ceil(datetime1), datetime1_ceil)

        # Lastly ensure everything works with Time as well:
        TimeSpan('1D').round(Time(2023,10,29,16,0,0))
        TimeSpan('1D').ceil(Time(2023,10,29,16,0,0))
        TimeSpan('1D').floor(Time(2023,10,29,16,0,0))
        TimeSpan('1D').shift(Time(2023,10,29,16,0,0))

        # Test the "slider"
        start = Time(2023,10,29,0,0,0, tz='Europe/Rome')
        end = start + TimeSpan('1D')

        slider = start
        while slider < end:
            slider = slider + TimeSpan('1h')

        self.assertEqual(slider, end)


    def test_operations(self):

        time_span_1 = TimeSpan('15m')
        time_span_2 = TimeSpan('15m_30.3s')
        time_span_3 = TimeSpan(days=1)

        # Sum with other TimeSpan objects
        self.assertEqual(str(time_span_1+time_span_2+time_span_3), '1D_30m_30.3s')

        # Sum with datetime (also on DST change)
        time_span = TimeSpan('1h')
        datetime1 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime2 = datetime1 + time_span
        datetime3 = datetime2 + time_span
        datetime4 = datetime3 + time_span
        datetime5 = datetime4 + time_span

        self.assertEqual(str(datetime1), '2015-10-25 00:15:00+02:00')
        self.assertEqual(str(datetime2), '2015-10-25 01:15:00+02:00')
        self.assertEqual(str(datetime3), '2015-10-25 02:15:00+02:00')
        self.assertEqual(str(datetime4), '2015-10-25 02:15:00+01:00')
        self.assertEqual(str(datetime5), '2015-10-25 03:15:00+01:00')

        # Sum a datetime (or anhything else other than another TimeSpan) to a TimeSpan: it does not make sense
        with self.assertRaises(NotImplementedError):
            TimeSpan('1h') + dt(2015,10,25,0,15,0, tz='Europe/Rome')

        # Sum with a numerical value
        time_span = TimeSpan('1h')
        epoch1 = 3600
        self.assertEqual(epoch1 + time_span, 7200)

        # Subtract to other TimeSpan object
        with self.assertRaises(NotImplementedError):
            time_span_1 - time_span_2

        # Subtract to a datetime object
        with self.assertRaises(NotImplementedError):
            time_span_1 - datetime1

        # In general, subtracting to anything is not implemented
        with self.assertRaises(NotImplementedError):
            time_span_1 - 'hello'

        # Subtract from a datetime (also on DST change)
        time_span = TimeSpan('1h')
        datetime1 = dt(2015,10,25,3,15,0, tz='Europe/Rome')
        datetime2 = datetime1 - time_span
        datetime3 = datetime2 - time_span
        datetime4 = datetime3 - time_span
        datetime5 = datetime4 - time_span

        self.assertEqual(str(datetime1), '2015-10-25 03:15:00+01:00')
        self.assertEqual(str(datetime2), '2015-10-25 02:15:00+01:00')
        self.assertEqual(str(datetime3), '2015-10-25 02:15:00+02:00')
        self.assertEqual(str(datetime4), '2015-10-25 01:15:00+02:00')
        self.assertEqual(str(datetime5), '2015-10-25 00:15:00+02:00')

        # Subtract from a numerical value
        time_span = TimeSpan('1h')
        epoch1 = 7200
        self.assertEqual(epoch1 - time_span, 3600)

        # Test sum with Time
        time_span = TimeSpan('1h')
        time = Time(60)
        self.assertEqual((time+time_span), 3660)

        # Test equal
        time_span_1 = TimeSpan('15m')
        self.assertEqual(time_span_1, 900)
