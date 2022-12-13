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

from gi.repository import Gtk

try:
    import unittest.mock as mock
except ImportError:
    import mock

from pyqso.ui.qso_dialog import AddQSODialog
from pyqso.adif import MODES, BANDS


class TestRecordDialog(unittest.TestCase):

    """The unit tests for the RecordDialog class."""

    def setUp(self):
        """Set up the objects needed for the unit tests."""
        PyQSO = mock.MagicMock()
        self.qso_dialog = AddQSODialog(application=PyQSO(), log=None)
        self.qso_dialog.frequency_unit = "MHz"

        # Set up the necessary sources.
        self.qso_dialog.sources["FREQ"] = Gtk.Entry()

        self.qso_dialog.sources["BAND"] = Gtk.ComboBoxText()
        for band in BANDS:
            self.qso_dialog.sources["BAND"].append_text(band)

        self.qso_dialog.sources["MODE"] = Gtk.ComboBoxText()
        for mode in sorted(MODES.keys()):
            self.qso_dialog.sources["MODE"].append_text(mode)

        self.qso_dialog.sources["SUBMODE"] = Gtk.ComboBoxText()
        self.qso_dialog.sources["SUBMODE"].append_text("")
        self.qso_dialog.sources["SUBMODE"].set_active(0)

        return

    def test_autocomplete_band(self):
        """Given a frequency, check that the band field is automatically set to the correct value."""
        self.qso_dialog.sources["FREQ"].set_text("145.525")
        self.qso_dialog.autocomplete_band()
        band = self.qso_dialog.sources["BAND"].get_active_text()
        assert band == "2m"

        self.qso_dialog.sources["FREQ"].set_text("9001")
        self.qso_dialog.autocomplete_band()
        band = self.qso_dialog.sources["BAND"].get_active_text()
        assert band == ""  # Frequency does not lie in any of the specified bands.

    def test_convert_frequency(self):
        """Check that a frequency can be successfully converted from one unit to another."""
        frequency = "7.140"  # In MHz
        converted = self.qso_dialog.convert_frequency(
            frequency, from_unit="MHz", to_unit="AHz"
        )  # Unknown to_unit. This should return the input unmodified (and give an error message).
        assert converted == frequency
        converted = self.qso_dialog.convert_frequency(
            frequency, from_unit="MHz", to_unit="kHz"
        )  # Convert from MHz to kHz.
        assert float(converted) == 1e3 * float(frequency)
        converted = self.qso_dialog.convert_frequency(
            converted, from_unit="kHz", to_unit="MHz"
        )  # Convert from kHz back to MHz. This should give the original frequency.
        assert float(converted) == float(frequency)

        # Floating-point data type.
        frequency = 7.140  # In MHz
        converted = self.qso_dialog.convert_frequency(
            frequency, from_unit="MHz", to_unit="kHz"
        )
        assert converted == frequency * 1e3

        # Floating-point data type.
        frequency = 7.140  # In MHz
        converted = self.qso_dialog.convert_frequency(
            frequency, from_unit="MHz", to_unit="MHz"
        )
        assert converted == frequency

        # Empty string.
        frequency = ""
        converted = self.qso_dialog.convert_frequency(
            frequency, from_unit="MHz", to_unit="kHz"
        )
        assert converted == frequency

        # Not a valid frequency.
        frequency = "HelloWorld"
        converted = self.qso_dialog.convert_frequency(
            frequency, from_unit="MHz", to_unit="kHz"
        )
        assert converted == frequency

    def test_hamlib_autofill(self):
        """Check that FREQ, MODE and SUBMODE information can be retrieved from Hamlib's dummy rig (if the Hamlib module exists)."""
        if have_hamlib:
            rig_model = "RIG_MODEL_DUMMY"
            rig_pathname = "/dev/Rig"
            self.qso_dialog.hamlib_autofill(rig_model, rig_pathname)
            assert self.qso_dialog.sources["FREQ"].get_text() == "145.000000"
            assert self.qso_dialog.sources["MODE"].get_active_text() == "FM"
            assert self.qso_dialog.sources["SUBMODE"].get_active_text() == ""
        else:
            pass


if __name__ == "__main__":
    unittest.main()
