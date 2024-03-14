# -*- coding: utf-8 -*-

import sys
import unittest
import datetime
import pytz
from ..utils import dt, correct_dt_dst, str_from_dt, dt_from_str, s_from_dt, dt_from_s, as_tz, timezonize, is_dt_ambiguous_without_offset
from ..time import Time
from dateutil.tz.tz import tzoffset
try:
    from zoneinfo import ZoneInfo
except:
    ZoneInfo = None

# Setup logging
from .. import logger
logger.setup()


class TestUtilities(unittest.TestCase):

    def test_timezonize(self):

        # Check pass through for time zone objects already valid
        pytz_time_zone = pytz.timezone('Europe/Rome')
        self.assertEqual(pytz_time_zone, timezonize(pytz_time_zone))

        offset = tzoffset(None, 3600)
        self.assertEqual(offset, timezonize(offset))

        if ZoneInfo:
            zone_info = ZoneInfo('Europe/Rome')
            self.assertEqual(zone_info, timezonize(zone_info))

        # Check correct conversion as pytz objects
        time_zone = timezonize(pytz.timezone('Europe/Rome'))
        self.assertEqual(str(time_zone), 'Europe/Rome')
        self.assertTrue(isinstance(time_zone, type(pytz.timezone('Europe/Rome'))))


    def test_correct_dt_dst(self):

        # 2015-03-29 01:15:00+01:00
        date_time =  dt(2015,3,29,1,15,0, tz='Europe/Rome')

        # 2015-03-29 02:15:00+01:00, Wrong on Europe/Rome and cannot be corrected as it does not exist
        date_time = date_time + datetime.timedelta(hours=1)
        with self.assertRaises(ValueError):
            correct_dt_dst(date_time)

        # 2015-03-29 03:15:00+01:00, Wrong on Europe/Rome but can be corrected
        date_time = date_time + datetime.timedelta(hours=1)
        self.assertEqual(correct_dt_dst(date_time), dt(2015,3,29,3,15,0, tz='Europe/Rome'))


    def test_dt(self):

        # Test Default
        date_time = dt(2015,3,29,2,15,0)
        self.assertEqual(str(date_time), '2015-03-29 02:15:00+00:00')

        # Test Naive
        date_time = dt(2015,3,29,2,15,0, naive=True)
        self.assertEqual(str(date_time), '2015-03-29 02:15:00')

        # Test with time zone (UTC)
        date_time = dt(2015,3,29,2,15,0, tz='UTC')
        self.assertEqual(str(date_time), '2015-03-29 02:15:00+00:00')

        # Test with time zone
        date_time = dt(2015,3,25,4,15,0, tz='Europe/Rome')
        self.assertEqual(str(date_time), '2015-03-25 04:15:00+01:00')
        date_time = dt(2015,9,25,4,15,0, tz='Europe/Rome')
        self.assertEqual(str(date_time), '2015-09-25 04:15:00+02:00')

        # Not existent time raises
        with self.assertRaises(ValueError):
            dt(2015,3,29,2,15,0, tz='Europe/Rome')

        # Ambiguous time
        with self.assertRaises(ValueError):
            dt(2015,10,25,2,15,0, tz='Europe/Rome')

        # Ambiguous time with guessing enabled (just raises a warning)
        date_time = dt(2015,10,25,2,15,0, tz='Europe/Rome', guessing=True)
        self.assertEqual(str(date_time), '2015-10-25 02:15:00+01:00')

        # Not existent time does not raises
        date_time = dt(2015,3,29,2,15,0, tz='Europe/Rome', trustme=True)
        self.assertEqual(date_time.year, 2015)
        self.assertEqual(date_time.month, 3)
        self.assertEqual(date_time.day, 29)
        self.assertEqual(date_time.hour, 2)
        self.assertEqual(date_time.minute, 15)
        self.assertEqual(str(date_time.tzinfo), 'Europe/Rome')

        # Very past years (no DST and messy time zones)
        date_time = dt(1856,12,1,16,46, tz='Europe/Rome')
        self.assertEqual(str(date_time), '1856-12-01 16:46:00+00:50')

        # NOTE: with pytz releases before ~ 2015.4 it was as follows:
        #self.assertEqual(str(date_time), '1856-12-01 16:46:00+01:00')

        date_time = dt(1926,12,1,16,46, tz='Europe/Rome')
        self.assertEqual(str(date_time), '1926-12-01 16:46:00+01:00')

        date_time = dt(1926,8,1,16,46, tz='Europe/Rome')
        self.assertEqual(str(date_time), '1926-08-01 16:46:00+01:00')

        # Very future years (no DST)
        date_time = dt(3567,12,1,16,46, tz='Europe/Rome')
        self.assertEqual(str(date_time), '3567-12-01 16:46:00+01:00')

        date_time = dt(3567,8,1,16,46, tz='Europe/Rome')
        self.assertEqual(str(date_time), '3567-08-01 16:46:00+01:00')


    def test_s_from_dt(self):

        date_time = dt(2001,12,1,16,46,10,6575, tz='Europe/Rome')
        self.assertEqual(s_from_dt(date_time), 1007221570.006575)

        # Naive datetime without the time zone and test conversion to epoch fails
        date_time = datetime.datetime.strptime('2007-12-10', '%Y-%m-%d')
        with self.assertRaises(ValueError):
            s_from_dt(date_time)

        # Naive datetime specifying on which time zone works
        date_time = dt(2023,12,3,16,12,0, naive=True)
        self.assertEqual(s_from_dt(date_time, tz='UTC'), 1701619920)

        # Naive datetime specifying on which time zone works
        date_time = dt(2023,12,3,16,12,0, naive=True)
        self.assertEqual(s_from_dt(date_time, tz='Europe/Rome'), 1701616320)

        # Sub-second offset
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
            self.assertEqual(s_from_dt(datetime.datetime(1986,8,1,15,6,34, tzinfo=tzoffset(None, 2.4))),523292791.6)
            self.assertEqual(s_from_dt(datetime.datetime(1986,8,1,15,6,34,100000, tzinfo=tzoffset(None, 2.4))),523292791.7)


    def test_dt_from_s(self):

        # Create a datetime from epoch seconds with no time zone (assume UTC)
        self.assertEqual(dt_from_s(1197244800), dt(2007,12,10,0,0, tz='UTC'))

        # Create a datetime from epoch seconds with a given time zone
        self.assertEqual(dt_from_s(900, tz='Europe/Rome'), dt(1970,1,1,1,15,0, tz='Europe/Rome'))

        # Create a datetime from epoch seconds with a given time zone as offset
        self.assertEqual(dt_from_s(900, tz=tzoffset(None,3600)), datetime.datetime(1970,1,1,1,15,0, tzinfo=tzoffset(None,3600)))

        if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
            # Create a datetime from epoch seconds with a given time zone as offset (sub-second)
            self.assertEqual(dt_from_s(900, tz=tzoffset(None,3600.1)), datetime.datetime(1970,1,1,1,15,0,100000, tzinfo=tzoffset(None,3600.1)))
            self.assertEqual(dt_from_s(900, tz=tzoffset(None,3600.01)), datetime.datetime(1970,1,1,1,15,0,10000, tzinfo=tzoffset(None,3600.01)))

    def test_str_conversions(self):

        # To ISO on UTC, offset is 0.
        self.assertEqual(str_from_dt(dt(1986,8,1,16,46, tz='UTC')), '1986-08-01T16:46:00+00:00')

        # To ISO on Europe/Rome, without DST, offset is +1.
        self.assertEqual(str_from_dt(dt(1986,12,1,16,46, tz='Europe/Rome')), '1986-12-01T16:46:00+01:00')

        # To ISO on Europe/Rome, with DST, offset is +2.
        self.assertEqual(str_from_dt(dt(1986,8,1,16,46, tz='Europe/Rome')), '1986-08-01T16:46:00+02:00')

        # From ISO on UTC
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00Z')), '1986-08-01 16:46:00+00:00')

        # From ISO as naive
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00')), '1986-08-01 16:46:00')

        # From ISO on offset +00:00
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00.362752+00:00')), '1986-08-01 16:46:00.362752+00:00')

        # From ISO on offset +02:00
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00.362752+02:00')), '1986-08-01 16:46:00.362752+02:00')

        # From ISO on offset +02:00 (with microseconds)
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00+02:00')), '1986-08-01 16:46:00+02:00')

        # From ISO on offset -07:00
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00-07:00')), '1986-08-01 16:46:00-07:00')

        # From ISO as naive with time zone
        self.assertEqual(str(dt_from_str('1986-08-01T16:46:00', tz='Europe/Rome')),'1986-08-01 16:46:00+02:00')

        # From ISO with a time zone set (tricky one, but correct)
        self.assertEqual(str(dt_from_str('2023-03-26 02:15:00+01:00', tz='Europe/Rome')), '2023-03-26 03:15:00+02:00')


    def test_as_tz(self):
        self.assertEqual(str(as_tz(dt_from_str('1986-08-01T16:46:00.362752+02:00'), 'UTC')), '1986-08-01 14:46:00.362752+00:00')


    def test_is_dt_ambiguous_without_offset(self):

        # Time zone: Europe/Rome. Expected results:
        # date_time_1 = 2023-10-29 01:15:00+02:00 -> False
        # date_time_2 = 2023-10-29 02:15:00+02:00 -> True
        # date_time_3 = 2023-10-29 02:15:00+01:00 -> True
        # date_time_4 = 2023-10-29 03:15:00+01:00 -> False
        start_epoch_s = s_from_dt(timezonize('UTC').localize(datetime.datetime(2023,10,28,23,15,0)))

        date_time_1 = dt_from_s(start_epoch_s, tz='Europe/Rome')
        self.assertFalse(is_dt_ambiguous_without_offset(date_time_1))

        date_time_2 = dt_from_s(start_epoch_s+3600, tz='Europe/Rome')
        self.assertTrue(is_dt_ambiguous_without_offset(date_time_2))

        date_time_3 = dt_from_s(start_epoch_s+3600*2, tz='Europe/Rome')
        self.assertTrue(is_dt_ambiguous_without_offset(date_time_3))

        date_time_4 = dt_from_s(start_epoch_s+3600*3, tz='Europe/Rome')
        self.assertFalse(is_dt_ambiguous_without_offset(date_time_4))

        # Time zone: America/New_York. Expected results:
        # date_time_1 = 2023-11-05 00:15:00-04:00 -> False
        # date_time_2 = 2023-11-05 01:15:00-04:00 -> True
        # date_time_3 = 2023-11-05 01:15:00-05:00 -> True
        # date_time_4 = 2023-11-05 02:15:00-05:00 -> False
        start_epoch_s = s_from_dt(timezonize('UTC').localize(datetime.datetime(2023,11,5,4,15,0)))

        date_time_1 = dt_from_s(start_epoch_s, tz='America/New_York')
        self.assertFalse(is_dt_ambiguous_without_offset(date_time_1))

        date_time_2 = dt_from_s(start_epoch_s+3600, tz='America/New_York')
        self.assertTrue(is_dt_ambiguous_without_offset(date_time_2))

        date_time_3 = dt_from_s(start_epoch_s+3600*2, tz='America/New_York')
        self.assertTrue(is_dt_ambiguous_without_offset(date_time_3))

        date_time_4 = dt_from_s(start_epoch_s+3600*3, tz='America/New_York')
        self.assertFalse(is_dt_ambiguous_without_offset(date_time_4))

