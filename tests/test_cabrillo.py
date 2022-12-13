#!/usr/bin/env python3

#    Copyright (C) 2017 Christian Thomas Jacobs.

#    This file is part of PyQSO.

#    PyQSO is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyQSO is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyQSO.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from pyqso.cabrillo import Cabrillo
from datetime import datetime


class TestCabrillo(unittest.TestCase):

    """The unit tests for the Cabrillo class."""

    def setUp(self):
        """Set up the Cabrillo object needed for the unit tests."""
        self.cabrillo = Cabrillo()
        return

    def test_convert_date_and_time_1(self):
        c = Cabrillo()
        date = "20220101"
        time = "1457"
        expected = datetime.strptime(f"{date} {time}", "%Y%m%d %H%M")

        assert c.convert_date_and_time(date, time) == expected


if __name__ == "__main__":
    unittest.main()
