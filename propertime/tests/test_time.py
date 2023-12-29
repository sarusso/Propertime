# -*- coding: utf-8 -*-

import unittest
import pytz
from datetime import datetime
from ..utils import dt, correct_dt_dst, str_from_dt, dt_from_str, s_from_dt, dt_from_s, as_tz, timezonize, now_s
from ..time import Time, TimeUnit
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

        # Time (UTC by default)
        time = Time(5.6)
        self.assertEqual(time, 5.6)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        # Time with offset
        time = Time(1702928535.0, offset=0)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 0)

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

        # Time with datetime-like arguments
        time = Time(2023,12,1)
        self.assertEqual(time, 1701388800.0)
        self.assertEqual(str(time.dt()), '2023-12-01 00:00:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')

        # Time with datetime-like arguments and time zone as argument
        time = Time(2023,12,1, tz='Europe/Rome')
        self.assertEqual(time, 1701385200.0)
        self.assertEqual(str(time.dt()), '2023-12-01 00:00:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time with datetime-like arguments and offset as argument
        time = Time(2023,12,1, offset=3600)
        self.assertEqual(time, 1701385200.0)
        self.assertEqual(str(time.dt()), '2023-12-01 00:00:00+01:00')
        self.assertEqual(time.tz, None)

        # Time with datetime-like arguments with both time zone and offset as arguments
        # Expected behavior: get on UTC given the offset and then treat as on the given time zone

        time = Time(2023, 6, 11, 17, 56, 0, offset=0, tz='UTC')
        self.assertEqual(str(time.dt()), '2023-06-11 17:56:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        time = Time(2023, 6, 11, 17, 56, 0, offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time.dt()), '2023-06-11 17:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # TODO: do we want this? Or do we want to ensure offset compatible with time zone?
        time = Time(2023, 6, 11, 17, 56, 0, offset=0, tz='Europe/Rome') # 17:56 UTC
        self.assertEqual(str(time.dt()), '2023-06-11 19:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # TODO: do we want this? Or do we want to ensure offset compatible with time zone?
        time = Time(2023, 6, 11, 17, 56, 0, offset=10800, tz='Europe/Rome') # 14:56 UTC
        self.assertEqual(str(time.dt()), '2023-06-11 16:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # Time from naive datetime (assumed as UTC)
        time = Time(dt(2023,12,3,16,12,0))
        self.assertEqual(time, 1701619920.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')

        # Time from naive datetime with time zone as argument
        # Expected behavior: treat as if on the given time zone
        time = Time(datetime(2023,12,3,16,12,0), tz='Europe/Rome')
        self.assertEqual(time, 1701616320.0)
        self.assertEqual(str(time.dt()), '2023-12-03 16:12:00+01:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')

        # Time from naive datetime with offset as argument
        # Expected behavior: treat as if with the given offset
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

        # Time from naive string with an extra (zero) offset
        # Expected behavior: treat as if with the given offset
        time = Time('2023-06-11T17:56:00', offset=0)
        self.assertEqual(time, 1686506160.0)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 0)

        # Time from naive string with an extra offset
        # Expected behavior: treat as if with the given offset
        time = Time('2023-06-11T17:56:00', offset=3600)
        self.assertEqual(time, 1686502560.0)
        self.assertEqual(time.tz, None)
        self.assertEqual(time.offset, 3600)

        # Time from string with a string on Zulu time
        time = Time('1986-08-01T16:46:00Z')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        # Time from string with an offset on UTC
        time = Time('1986-08-01T16:46:00+00:00')
        self.assertEqual(time, 523298760.0)
        self.assertEqual(time.offset, 0)
        self.assertEqual(time.tz, None)

        # Time from string with a different offset
        time = Time('2023-12-25T16:12:00+01:00')
        self.assertEqual(time, 1703517120.0)
        self.assertEqual(time.offset, 3600)
        self.assertEqual(time.tz, None)

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

        # Time from string with an offset and both an extra offset and time zone as arguments
        # Expected behavior: get on UTC given the offset and then treat as on the given time zone

        time = Time('2023-06-11T17:56:00+00:00', offset=0, tz='UTC')
        self.assertEqual(str(time.dt()), '2023-06-11 17:56:00+00:00')
        self.assertEqual(str(time.tz), 'UTC')
        self.assertEqual(time.offset, 0)

        time = Time('2023-06-11T17:56:00+00:00', offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time.dt()), '2023-06-11 19:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # TODO: do we want this? Or do we want to ensure offset compatible with time zone?
        time = Time('2023-06-11T17:56:00+00:00', offset=0, tz='Europe/Rome') # 17:56 UTC
        self.assertEqual(str(time.dt()), '2023-06-11 19:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

        # TODO: do we want this? Or do we want to ensure offset compatible with time zone?
        time = Time('2023-06-11T17:56:00+03:00', offset=10800, tz='Europe/Rome') # 14:56 UTC
        self.assertEqual(str(time.dt()), '2023-06-11 16:56:00+02:00')
        self.assertEqual(str(time.tz), 'Europe/Rome')
        self.assertEqual(time.offset, 7200)

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
        time = Time(2023,10,29,2,15,0, tz='Europe/Rome', can_guess=True)
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')
        self.assertEqual(time.iso(), '2023-10-29T02:15:00+01:00')

        # Ambiguous time with offset OK
        time = Time(2023,10,29,2,15,0, offset=3600, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')
        self.assertEqual(time.iso(), '2023-10-29T02:15:00+01:00')

        time = Time(2023,10,29,2,15,0, offset=7200, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698538500.0 (2023-10-29 02:15:00 Europe/Rome DST)')
        self.assertEqual(time.iso(), '2023-10-29T02:15:00+02:00')

        # Extra check for string init on ambiguous time (TODO: maybe move elsewhere?)
        time = Time('2023-10-29T02:15:00+01:00', tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698542100.0 (2023-10-29 02:15:00 Europe/Rome)')

        time = Time('2023-10-29T02:15:00+02:00', tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1698538500.0 (2023-10-29 02:15:00 Europe/Rome DST)')


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

        # Negative offset
        time = Time(1702928535.0, offset=-68400)
        self.assertEqual(str(time), 'Time: 1702928535.0 (2023-12-18 00:42:15 -19:00)')

        # Offset non-hourly and sub-second
        time = Time(523291560, offset=3546.0945)
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:45:06 +00:59:06.094500)')

        # Time zone
        time = Time(1702928535.0, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 1702928535.0 (2023-12-18 20:42:15 Europe/Rome)')

        # Time zone plus DST
        time = Time(523291560, tz='Europe/Rome')
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')



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
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')
        self.assertEqual(time.offset, 7200)
        time.tz = 'America/New_York'
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 10:46:00 America/New_York DST)')
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
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 16:46:00 Europe/Rome DST)')
        time.offset = 3600
        self.assertEqual(str(time), 'Time: 523291560.0 (1986-08-01 15:46:00 +01:00)')
        self.assertEqual(time.tz, None)


    def test_operations(self):

        # Operations
        time1 = Time(4.3)
        time2 = Time(4.2)
        self.assertEqual(time1 + time2, 8.5)



class TestTimeUnits(unittest.TestCase):

    def test_TimeUnit(self):

        with self.assertRaises(ValueError):
            _ = TimeUnit('15m', '20s')

        # Not valid 'q' type
        with self.assertRaises(ValueError):
            _ = TimeUnit('15q')

        # Numerical init
        time_unit_1 = TimeUnit(60)
        self.assertEqual(str(time_unit_1), '60s')

        # String init
        time_unit_1 = TimeUnit('15m')
        self.assertEqual(str(time_unit_1), '15m')

        time_unit_2 = TimeUnit('15m_30s_3u')
        self.assertEqual(str(time_unit_2), '15m_30s_3u')

        # Components init
        self.assertEqual(TimeUnit(days=1).days, 1)
        self.assertEqual(TimeUnit(years=2).years, 2)
        self.assertEqual(TimeUnit(minutes=1).minutes, 1)
        self.assertEqual(TimeUnit(minutes=15).minutes, 15)
        self.assertEqual(TimeUnit(hours=1).hours, 1)

        # Test various init and correct handling of time componentes
        self.assertEqual(TimeUnit('1D').days, 1)
        self.assertEqual(TimeUnit('2Y').years, 2)
        self.assertEqual(TimeUnit('1m').minutes, 1)
        self.assertEqual(TimeUnit('15m').minutes, 15)
        self.assertEqual(TimeUnit('1h').hours, 1)

        # Test floating point seconds init
        self.assertEqual(TimeUnit('1.2345s').as_seconds(), 1.2345)
        self.assertEqual(TimeUnit('1.234s').as_seconds(), 1.234)
        self.assertEqual(TimeUnit('1.02s').as_seconds(), 1.02)
        self.assertEqual(TimeUnit('1.000005s').as_seconds(), 1.000005)
        self.assertEqual(TimeUnit('67.000005s').seconds, 67)
        self.assertEqual(TimeUnit('67.000005s').microseconds, 5)
  
        # Too much precision (below microseconds), gets cut
        time_unit = TimeUnit('1.0000005s')
        self.assertEqual(str(time_unit),'1s')
        time_unit = TimeUnit('1.0000065s')
        self.assertEqual(str(time_unit),'1s_6u')

        # Test unit values
        self.assertEqual(TimeUnit(600).value, '600s') # Int converted to string representation
        self.assertEqual(TimeUnit(600.0).value, '600s') # Float converted to string representation
        self.assertEqual(TimeUnit(600.45).value, '600s_450000u') # Float converted to string representation (using microseconds)

        self.assertEqual(TimeUnit(days=1).value, '1D')
        self.assertEqual(TimeUnit(years=2).value, '2Y')
        self.assertEqual(TimeUnit(minutes=1).value, '1m')
        self.assertEqual(TimeUnit(minutes=15).value, '15m')
        self.assertEqual(TimeUnit(hours=1).value, '1h')

        self.assertEqual(time_unit_1.value, '15m')
        self.assertEqual(time_unit_2.value, '15m_30s_3u') 
        self.assertEqual(TimeUnit(days=1).value, '1D') # This is obtained using the unit's string representation

        # Test unit equalities and inequalities 
        self.assertTrue(TimeUnit(hours=1) == TimeUnit(hours=1))
        self.assertTrue(TimeUnit(hours=1) == '1h')
        self.assertFalse(TimeUnit(hours=1) == TimeUnit(hours=2))
        self.assertFalse(TimeUnit(hours=1) == 'a_string')

        self.assertTrue(TimeUnit(days=1) == TimeUnit(days=1))
        self.assertTrue(TimeUnit(days=1) == '1D')
        self.assertFalse(TimeUnit(days=1) == TimeUnit(days=2))
        self.assertFalse(TimeUnit(days=1) == 'a_string')

        self.assertFalse(TimeUnit('86400s') == TimeUnit('1D'))


    def test_TimeUnit_math(self):

        time_unit_1 = TimeUnit('15m')
        time_unit_2 = TimeUnit('15m_30s_3u')
        time_unit_3 = TimeUnit(days=1)

        # Sum with other TimeUnit objects
        self.assertEqual(str(time_unit_1+time_unit_2+time_unit_3), '1D_30m_30s_3u')

        # Sum with datetime (also on DST change)
        time_unit = TimeUnit('1h')
        datetime1 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime2 = datetime1 + time_unit
        datetime3 = datetime2 + time_unit
        datetime4 = datetime3 + time_unit
        datetime5 = datetime4 + time_unit

        self.assertEqual(str(datetime1), '2015-10-25 00:15:00+02:00')
        self.assertEqual(str(datetime2), '2015-10-25 01:15:00+02:00')
        self.assertEqual(str(datetime3), '2015-10-25 02:15:00+02:00')
        self.assertEqual(str(datetime4), '2015-10-25 02:15:00+01:00')
        self.assertEqual(str(datetime5), '2015-10-25 03:15:00+01:00')

        # Sum with a numerical value
        time_unit = TimeUnit('1h')
        epoch1 = 3600
        self.assertEqual(epoch1 + time_unit, 7200)

        # Subtract to other TimeUnit object
        with self.assertRaises(NotImplementedError):
            time_unit_1 - time_unit_2

        # Subtract to a datetime object
        with self.assertRaises(NotImplementedError):
            time_unit_1 - datetime1

        # In general, subtracting to anything is not implemented
        with self.assertRaises(NotImplementedError):
            time_unit_1 - 'hello'

        # Subtract from a datetime (also on DST change)
        time_unit = TimeUnit('1h')
        datetime1 = dt(2015,10,25,3,15,0, tz='Europe/Rome')
        datetime2 = datetime1 - time_unit
        datetime3 = datetime2 - time_unit
        datetime4 = datetime3 - time_unit
        datetime5 = datetime4 - time_unit

        self.assertEqual(str(datetime1), '2015-10-25 03:15:00+01:00')
        self.assertEqual(str(datetime2), '2015-10-25 02:15:00+01:00')
        self.assertEqual(str(datetime3), '2015-10-25 02:15:00+02:00')
        self.assertEqual(str(datetime4), '2015-10-25 01:15:00+02:00')
        self.assertEqual(str(datetime5), '2015-10-25 00:15:00+02:00')

        # Subtract from a numerical value
        time_unit = TimeUnit('1h')
        epoch1 = 7200
        self.assertEqual(epoch1 - time_unit, 3600)

        # Test sum with Time
        time_unit = TimeUnit('1h')
        time = Time(60)
        self.assertEqual((time+time_unit), 3660)

        # Test equal
        time_unit_1 = TimeUnit('15m')
        self.assertEqual(time_unit_1, 900)


    def test_TimeUnit_types(self):

        # Test type
        self.assertEqual(TimeUnit('15m').type, TimeUnit._PHYSICAL)
        self.assertEqual(TimeUnit('1h').type, TimeUnit._PHYSICAL)
        self.assertEqual(TimeUnit('1D').type, TimeUnit._CALENDAR)
        self.assertEqual(TimeUnit('1M').type, TimeUnit._CALENDAR)


    def test_TimeUnit_duration(self):

        datetime1 = dt(2015,10,24,0,15,0, tz='Europe/Rome')
        datetime2 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime3 = dt(2015,10,26,0,15,0, tz='Europe/Rome')
 
        # Day unit
        time_unit = TimeUnit('1D')
        with self.assertRaises(ValueError):
            time_unit.as_seconds()
        self.assertEqual(time_unit.as_seconds(datetime1), 86400) # No DST, standard day
        self.assertEqual(time_unit.as_seconds(datetime2), 90000) # DST, change

        # Week unit
        time_unit = TimeUnit('1W')
        with self.assertRaises(ValueError):
            time_unit.as_seconds()
        self.assertEqual(time_unit.as_seconds(datetime1), (86400*7)+3600)
        self.assertEqual(time_unit.as_seconds(datetime3), (86400*7))

        # Month Unit
        time_unit = TimeUnit('1M')
        with self.assertRaises(ValueError):
            time_unit.as_seconds()
        self.assertEqual(time_unit.as_seconds(datetime3), (86400*31)) # October has 31 days so next month same day has 31 full days
        self.assertEqual(time_unit.as_seconds(datetime1), ((86400*31)+3600)) # Same as above, but in this case we have a DST change in the middle

        # Year Unit
        time_unit = TimeUnit('1Y')
        with self.assertRaises(ValueError):
            time_unit.as_seconds()
        self.assertEqual(time_unit.as_seconds(dt(2014,10,24,0,15,0, tz='Europe/Rome')), (86400*365)) # Standard year
        self.assertEqual(time_unit.as_seconds(dt(2015,10,24,0,15,0, tz='Europe/Rome')), (86400*366)) # Leap year

        # Test duration with composite seconds init
        self.assertEqual(TimeUnit(minutes=1, seconds=3).as_seconds(), 63)


    def test_TimeUnit_shift(self):

        datetime1 = dt(2015,10,24,0,15,0, tz='Europe/Rome')
        datetime2 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime3 = dt(2015,10,26,0,15,0, tz='Europe/Rome')

        # Day unit
        time_unit = TimeUnit('1D')
        self.assertEqual(time_unit.shift(datetime1), dt(2015,10,25,0,15,0, tz='Europe/Rome')) # No DST, standard day
        self.assertEqual(time_unit.shift(datetime2), dt(2015,10,26,0,15,0, tz='Europe/Rome')) # DST, change

        # Day unit on not-existent hour due to DST
        starting_dt = dt(2023,3,25,2,15, tz='Europe/Rome')
        with self.assertRaises(ValueError):
            starting_dt + TimeUnit('1D')

        # Day unit on ambiguous hour due to DST
        starting_dt = dt(2023,10,28,2,15, tz='Europe/Rome')
        with self.assertRaises(ValueError):
            starting_dt + TimeUnit('1D')

        # Week unit
        time_unit = TimeUnit('1W')
        self.assertEqual(time_unit.shift(datetime1), dt(2015,10,31,0,15,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.shift(datetime3), dt(2015,11,2,0,15,0, tz='Europe/Rome'))

        # Month Unit
        time_unit = TimeUnit('1M')
        self.assertEqual(time_unit.shift(datetime1), dt(2015,11,24,0,15,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.shift(datetime2), dt(2015,11,25,0,15,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.shift(datetime3), dt(2015,11,26,0,15,0, tz='Europe/Rome'))

        # Test 12%12 must give 12 edge case
        self.assertEqual(time_unit.shift(dt(2015,1,1,0,0,0, tz='Europe/Rome')), dt(2015,2,1,0,0,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.shift(dt(2015,11,1,0,0,0, tz='Europe/Rome')), dt(2015,12,1,0,0,0, tz='Europe/Rome'))

        # Year Unit
        time_unit = TimeUnit('1Y')
        self.assertEqual(time_unit.shift(datetime1), dt(2016,10,24,0,15,0, tz='Europe/Rome'))


    def test_TimeUnit_operations(self):

        # Test that complex time_units are not handable
        time_unit = TimeUnit('1D_3h_5m')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome')

        with self.assertRaises(ValueError):
            _ = time_unit.floor(datetime)

        # Test in ceil/floor/round normal conditions (days)
        time_unit = TimeUnit('1D')
        self.assertEqual(time_unit.ceil(dt(2023,11,25,10,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,11,26,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.floor(dt(2023,11,25,19,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,11,25,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.round(dt(2023,11,25,10,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,11,25,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.round(dt(2023,11,25,12,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,11,25,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.round(dt(2023,11,25,13,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,11,26,0,0,0, tz='Europe/Rome')))

        # Test in ceil/floor/round across DST change (days)
        time_unit = TimeUnit('1D')
        self.assertEqual(time_unit.ceil(dt(2023,3,26,10,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,3,27,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.floor(dt(2023,3,26,19,0,0, tz='Europe/Rome')), time_unit.round(dt(2023,3,26,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.round(dt(2023,3,26,12,30,0, tz='Europe/Rome')), time_unit.round(dt(2023,3,26,0,0,0, tz='Europe/Rome')))
        self.assertEqual(time_unit.round(dt(2023,3,26,12,31,0, tz='Europe/Rome')), time_unit.round(dt(2023,3,27,0,0,0, tz='Europe/Rome')))

        # Test in ceil/floor/round normal conditions (hours)
        time_unit = TimeUnit('1h')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome')
        self.assertEqual(time_unit.floor(datetime), dt(2015,1,1,16,0,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.ceil(datetime), dt(2015,1,1,17,0,0, tz='Europe/Rome'))

        # Test in ceil/floor/round normal conditions (minutes)
        time_unit = TimeUnit('15m')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome')
        self.assertEqual(time_unit.floor(datetime), dt(2015,1,1,16,30,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.ceil(datetime), dt(2015,1,1,16,45,0, tz='Europe/Rome'))

        # Test ceil/floor/round in normal conditions (seconds)
        time_unit = TimeUnit('30s')
        datetime = dt(2015,1,1,16,37,14, tz='Europe/Rome') 
        self.assertEqual(time_unit.floor(datetime), dt(2015,1,1,16,37,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.ceil(datetime), dt(2015,1,1,16,37,30, tz='Europe/Rome'))

        # Test ceil/floor/round across 1970-1-1 (minutes) 
        time_unit = TimeUnit('5m')
        datetime1 = dt(1969,12,31,23,57,29, tz='UTC') # epoch = -3601
        datetime2 = dt(1969,12,31,23,59,59, tz='UTC') # epoch = -3601
        self.assertEqual(time_unit.floor(datetime1), dt(1969,12,31,23,55,0, tz='UTC'))
        self.assertEqual(time_unit.ceil(datetime1), dt(1970,1,1,0,0, tz='UTC'))
        self.assertEqual(time_unit.round(datetime1), dt(1969,12,31,23,55,0, tz='UTC'))
        self.assertEqual(time_unit.round(datetime2), dt(1970,1,1,0,0, tz='UTC'))

        # Test ceil/floor/round (3 hours-test)
        time_unit = TimeUnit('3h')
        datetime = dt(1969,12,31,23,0,1, tz='Europe/Rome') # negative epoch
        self.assertEqual(time_unit.floor(datetime), dt(1969,12,31,23,0,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.ceil(datetime), dt(1970,1,1,2,0, tz='Europe/Rome'))

        # Test ceil/floor/round across 1970-1-1 (together with the 2 hours-test, TODO: decouple) 
        time_unit = TimeUnit('2h')
        datetime1 = dt(1969,12,31,22,59,59, tz='Europe/Rome') # negative epoch
        datetime2 = dt(1969,12,31,23,0,1, tz='Europe/Rome') # negative epoch  
        self.assertEqual(time_unit.floor(datetime1), dt(1969,12,31,22,0,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.ceil(datetime1), dt(1970,1,1,0,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.round(datetime1), dt(1969,12,31,22,0, tz='Europe/Rome'))
        self.assertEqual(time_unit.round(datetime2), dt(1970,1,1,0,0, tz='Europe/Rome'))

        # Test ceil/floor/round across DST change (hours)
        time_unit = TimeUnit('1h')

        datetime1 = dt(2015,10,25,0,15,0, tz='Europe/Rome')
        datetime2 = datetime1 + time_unit    # 2015-10-25 01:15:00+02:00
        datetime3 = datetime2 + time_unit    # 2015-10-25 02:15:00+02:00
        datetime4 = datetime3 + time_unit    # 2015-10-25 02:15:00+01:00

        datetime1_rounded = dt(2015,10,25,0,0,0, tz='Europe/Rome')
        datetime2_rounded = datetime1_rounded + time_unit
        datetime3_rounded = datetime2_rounded + time_unit
        datetime4_rounded = datetime3_rounded + time_unit
        datetime5_rounded = datetime4_rounded + time_unit

        self.assertEqual(time_unit.floor(datetime2), datetime2_rounded)
        self.assertEqual(time_unit.ceil(datetime2), datetime3_rounded)

        self.assertEqual(time_unit.floor(datetime3), datetime3_rounded)
        self.assertEqual(time_unit.ceil(datetime3), datetime4_rounded)

        self.assertEqual(time_unit.floor(datetime4), datetime4_rounded)
        self.assertEqual(time_unit.ceil(datetime4), datetime5_rounded)

        # Test ceil/floor/round with a calendar time unit and across a DST change

        # Day unit
        time_unit = TimeUnit('1D')

        datetime1 = dt(2015,10,25,4,15,34, tz='Europe/Rome') # DST off (+01:00)
        datetime1_floor = dt(2015,10,25,0,0,0, tz='Europe/Rome') # DST on (+02:00)
        datetime1_ceil = dt(2015,10,26,0,0,0, tz='Europe/Rome') # DST off (+01:00)

        self.assertEqual(time_unit.floor(datetime1), datetime1_floor)
        self.assertEqual(time_unit.ceil(datetime1), datetime1_ceil)

        # Week unit
        time_unit = TimeUnit('1W')

        datetime1 = dt(2023,10,29,15,47, tz='Europe/Rome') # DST off (+01:00)
        datetime1_floor = dt(2023,10,23,0,0, tz='Europe/Rome') # DST on (+02:00)
        datetime1_ceil = dt(2023,10,30,0,0, tz='Europe/Rome') # DST off (+01:00)

        self.assertEqual(time_unit.floor(datetime1), datetime1_floor)
        self.assertEqual(time_unit.ceil(datetime1), datetime1_ceil)

        # Month unit
        time_unit = TimeUnit('1M')

        datetime1 = dt(2015,10,25,4,15,34, tz='Europe/Rome') # DST off (+01:00)
        datetime1_floor = dt(2015,10,1,0,0,0, tz='Europe/Rome') # DST on (+02:00)
        datetime1_ceil = dt(2015,11,1,0,0,0, tz='Europe/Rome') # DST off (+01:00)

        self.assertEqual(time_unit.floor(datetime1), datetime1_floor)
        self.assertEqual(time_unit.ceil(datetime1), datetime1_ceil)

        # Year unit
        time_unit = TimeUnit('1Y')

        datetime1 = dt(2015,10,25,4,15,34, tz='Europe/Rome')
        datetime1_floor = dt(2015,1,1,0,0,0, tz='Europe/Rome')
        datetime1_ceil = dt(2016,1,1,0,0,0, tz='Europe/Rome')

        self.assertEqual(time_unit.floor(datetime1), datetime1_floor)
        self.assertEqual(time_unit.ceil(datetime1), datetime1_ceil)

