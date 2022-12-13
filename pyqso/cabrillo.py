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

import logging
from datetime import datetime

import cabrillo

CABRILLO_VERSION = "3.0"


class Cabrillo:

    """The Cabrillo class supplies methods for writing log files in the Cabrillo format (v3.0).
    For more information, visit http://wwrof.org/cabrillo/"""

    def __init__(self):
        """Initialise class for I/O of files using the Cabrillo format."""
        return

    def convert_date_and_time(self, date, time):
        """Converts the date format used internally (YYYYMMDD, used due to ADIF) to
        the format used by Cabrillo (YYYY-MM-DD)"""

        return datetime.strptime(f"{date} {time}", "%Y%m%d %H%M")

    def get_contest_exchange(self, r, contest):

        # Just an example, needs to be dynamic and lookup contests from a data
        # store

        rst_sent = r["RST_SENT"]
        rst_rcvd = r["RST_RCVD"]

        if contest == "ARRL-10":
            if r["DE_CONTEST_SERIAL"]:
                de_qth_serial = r["DE_CONTEST_SERIAL"]
            else:
                de_qth_serial = r["DE_STATE"]

            if r["DX_CONTEST_SERIAL"]:
                dx_qth_serial = r["DX_CONTEST_SERIAL"]
            else:
                dx_qth_serial = r["DX_STATE"]

            de_exchange = [rst_sent, de_qth_serial]
            dx_exchange = [rst_sent, dx_qth_serial]

        return de_exchange, dx_echange


    def write(self, qsos, path, contest="", mycall=""):
        """Write a list of QSOs to a file in the Cabrillo format.

        :arg list qsos: The list of QSOs to write.
        :arg str path: The desired path of the Cabrillo file to write to.
        :arg str contest: The name of the contest.
        :arg str mycall: The callsign used during the contest.
        :returns: None
        :raises IOError: If the Cabrillo file cannot be written (e.g. due to lack of write permissions)."""

        logging.debug("Writing QSOs to a Cabrillo file...")

        cabrillo_log = cabrillo.Cabrillo(version=CABRILLO_VERSION, callsign=mycall, contest=contest)

        # Write each QSO to the file.
        for r in qsos:

            # TODO: replace with a conversion function added to util.py
            # Frequency. Note that this must be in kHz. The frequency is stored in MHz in the database, so it's converted to kHz here.
            try:
                freq = str(float(r["FREQ"]) * 1e3)
            except ValueError:
                freq = ""

            # Mode
            if r["MODE"] == "SSB":
                mode = "PH"
            elif r["MODE"] == "CW":
                mode = "CW"
            elif r["MODE"] == "FM":
                mode = "FM"
            else:
                # TODO: Github Issue #28 - This assumes that the mode is any other non-CW digital mode, which isn't always going to be the case (e.g. for AM).
                mode = "RY"

            # Transmitter ID (must be 0 or 1, if applicable).
            # FIXME: For now this has been hard-coded to 0.
            t = "0"

            rst_sent = r["RST_SENT"]
            rst_rcvd = r["RST_RCVD"]

            # The format of exchange that is sent and received varies based on
            # the contest, and is left open-ended in the Cabrillo specification
            # accordingly.

            #if contest:
            #    de_exch, dx_exch = self.get_contest_exchange(r, contest)

            # If there isn't a contest, the default exchange is just an RST.
            de_exch = [rst_sent]
            dx_exch = [rst_rcvd]

            qso = cabrillo.QSO(freq, mode, self.convert_date_and_time(r["QSO_DATE"], r["TIME_ON"]), mycall, r["CALL"], de_exch, dx_exch, t)
            cabrillo_log.append_qso(qso, ignore_order=True)

        with open(path, mode='w', errors="replace") as f:
            cabrillo_log.write(f)

        logging.info("Wrote %d QSOs to %s in Cabrillo format." % (len(qsos), path))

        return
