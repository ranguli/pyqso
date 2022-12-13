#!/usr/bin/env python3

#    Copyright (C) 2012-2017 Christian Thomas Jacobs.

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

import re
import logging
import calendar

# ADIF field names and their associated data types available in PyQSO.
AVAILABLE_FIELD_NAMES_TYPES = {
    "CALL": "S",
    "QSO_DATE": "D",
    "TIME_ON": "T",
    "FREQ": "N",
    "BAND": "E",
    "MODE": "E",
    "SUBMODE": "E",
    "PROP_MODE": "E",
    "TX_PWR": "N",
    "RST_SENT": "S",
    "RST_RCVD": "S",
    "QSL_SENT": "S",
    "QSL_RCVD": "S",
    "NOTES": "M",
    "NAME": "S",
    "ADDRESS": "S",
    "STATE": "S",
    "COUNTRY": "S",
    "DXCC": "N",
    "CQZ": "N",
    "ITUZ": "N",
    "IOTA": "C",
    "GRIDSQUARE": "S",
    "SAT_NAME": "S",
    "SAT_MODE": "S",
}
# Note: The logbook uses the ADIF field names for the database column names.
# This list is used to display the columns in a logical order.
AVAILABLE_FIELD_NAMES_ORDERED = [
    "CALL",
    "QSO_DATE",
    "TIME_ON",
    "FREQ",
    "BAND",
    "MODE",
    "SUBMODE",
    "PROP_MODE",
    "TX_PWR",
    "RST_SENT",
    "RST_RCVD",
    "QSL_SENT",
    "QSL_RCVD",
    "NOTES",
    "NAME",
    "ADDRESS",
    "STATE",
    "COUNTRY",
    "DXCC",
    "CQZ",
    "ITUZ",
    "IOTA",
    "GRIDSQUARE",
    "SAT_NAME",
    "SAT_MODE",
]
# Define the more user-friendly versions of the field names.
AVAILABLE_FIELD_NAMES_FRIENDLY = {
    "CALL": "Callsign",
    "QSO_DATE": "Date",
    "TIME_ON": "Time",
    "FREQ": "Frequency (MHz)",
    "BAND": "Band",
    "MODE": "Mode",
    "SUBMODE": "Submode",
    "PROP_MODE": "Propagation Mode",
    "TX_PWR": "TX Power (W)",
    "RST_SENT": "RST Sent",
    "RST_RCVD": "RST Received",
    "QSL_SENT": "QSL Sent",
    "QSL_RCVD": "QSL Received",
    "NOTES": "Notes",
    "NAME": "Name",
    "ADDRESS": "Address",
    "STATE": "State",
    "COUNTRY": "Country",
    "DXCC": "DXCC",
    "CQZ": "CQ Zone",
    "ITUZ": "ITU Zone",
    "IOTA": "IOTA Designator",
    "GRIDSQUARE": "Grid Square",
    "SAT_NAME": "Satellite Name",
    "SAT_MODE": "Satellite Mode",
}

# All the valid modes listed in the ADIF specification. This is a dictionary with the key-value pairs holding the MODE and SUBMODE(s) respectively.
MODES = {
    "": ("",),
    "AM": ("",),
    "ATV": ("",),
    "CHIP": ("", "CHIP64", "CHIP128"),
    "CLO": ("",),
    "CONTESTI": ("",),
    "CW": ("", "PCW"),
    "DIGITALVOICE": ("",),
    "DOMINO": ("", "DOMINOEX", "DOMINOF"),
    "DSTAR": ("",),
    "FAX": ("",),
    "FM": ("",),
    "FSK441": ("",),
    "FT8": ("",),
    "HELL": ("", "FMHELL", "FSKHELL", "HELL80", "HFSK", "PSKHELL"),
    "ISCAT": ("", "ISCAT-A", "ISCAT-B"),
    "JT4": ("", "JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G"),
    "JT6M": ("",),
    "JT9": ("",),
    "JT44": ("",),
    "JT65": ("", "JT65A", "JT65B", "JT65B2", "JT65C", "JT65C2"),
    "MFSK": (
        "",
        "MFSK4",
        "MFSK8",
        "MFSK11",
        "MFSK16",
        "MFSK22",
        "MFSK31",
        "MFSK32",
        "MFSK64",
        "MFSK128",
    ),
    "MT63": ("",),
    "OLIVIA": (
        "",
        "OLIVIA 4/125",
        "OLIVIA 4/250",
        "OLIVIA 8/250",
        "OLIVIA 8/500",
        "OLIVIA 16/500",
        "OLIVIA 16/1000",
        "OLIVIA 32/1000",
    ),
    "OPERA": ("", "OPERA-BEACON", "OPERA-QSO"),
    "PAC": ("", "PAC2", "PAC3", "PAC4"),
    "PAX": ("", "PAX2"),
    "PKT": ("",),
    "PSK": (
        "",
        "FSK31",
        "PSK10",
        "PSK31",
        "PSK63",
        "PSK63F",
        "PSK125",
        "PSK250",
        "PSK500",
        "PSK1000",
        "PSKAM10",
        "PSKAM31",
        "PSKAM50",
        "PSKFEC31",
        "QPSK31",
        "QPSK63",
        "QPSK125",
        "QPSK250",
        "QPSK500",
    ),
    "PSK2K": ("",),
    "Q15": ("",),
    "ROS": ("", "ROS-EME", "ROS-HF", "ROS-MF"),
    "RTTY": ("", "ASCI"),
    "RTTYM": ("",),
    "SSB": ("", "LSB", "USB"),
    "SSTV": ("",),
    "THOR": ("",),
    "THRB": ("", "THRBX"),
    "TOR": ("", "AMTORFEC", "GTOR"),
    "V4": ("",),
    "VOI": ("",),
    "WINMOR": ("",),
    "WSPR": ("",),
}

# A dictionary of all the deprecated MODE values.
MODES_DEPRECATED = {
    "AMTORFEC": ("",),
    "ASCI": ("",),
    "CHIP64": ("",),
    "CHIP128": ("",),
    "DOMINOF": ("",),
    "FMHELL": ("",),
    "FSK31": ("",),
    "GTOR": ("",),
    "HELL80": ("",),
    "HFSK": ("",),
    "JT4A": ("",),
    "JT4B": ("",),
    "JT4C": ("",),
    "JT4D": ("",),
    "JT4E": ("",),
    "JT4F": ("",),
    "JT4G": ("",),
    "JT65A": ("",),
    "JT65B": ("",),
    "JT65C": ("",),
    "MFSK8": ("",),
    "MFSK16": ("",),
    "PAC2": ("",),
    "PAC3": ("",),
    "PAX2": ("",),
    "PCW": ("",),
    "PSK10": ("",),
    "PSK31": ("",),
    "PSK63": ("",),
    "PSK63F": ("",),
    "PSK125": ("",),
    "PSKAM10": ("",),
    "PSKAM31": ("",),
    "PSKAM50": ("",),
    "PSKFEC31": ("",),
    "PSKHELL": ("",),
    "QPSK31": ("",),
    "QPSK63": ("",),
    "QPSK125": ("",),
    "THRBX": ("",),
}

# Include all deprecated modes.
MODES.update(MODES_DEPRECATED)

# All the bands listed in the ADIF specification.
BANDS = [
    "",
    "2190m",
    "630m",
    "560m",
    "160m",
    "80m",
    "60m",
    "40m",
    "30m",
    "20m",
    "17m",
    "15m",
    "12m",
    "10m",
    "6m",
    "4m",
    "2m",
    "1.25m",
    "70cm",
    "33cm",
    "23cm",
    "13cm",
    "9cm",
    "6cm",
    "3cm",
    "1.25cm",
    "6mm",
    "4mm",
    "2.5mm",
    "2mm",
    "1mm",
]
# The lower and upper frequency bounds (in MHz) for each band in BANDS.
BANDS_RANGES = [
    (None, None),
    (0.136, 0.137),
    (0.472, 0.479),
    (0.501, 0.504),
    (1.8, 2.0),
    (3.5, 4.0),
    (5.102, 5.4065),
    (7.0, 7.3),
    (10.0, 10.15),
    (14.0, 14.35),
    (18.068, 18.168),
    (21.0, 21.45),
    (24.890, 24.99),
    (28.0, 29.7),
    (50.0, 54.0),
    (70.0, 71.0),
    (144.0, 148.0),
    (222.0, 225.0),
    (420.0, 450.0),
    (902.0, 928.0),
    (1240.0, 1300.0),
    (2300.0, 2450.0),
    (3300.0, 3500.0),
    (5650.0, 5925.0),
    (10000.0, 10500.0),
    (24000.0, 24250.0),
    (47000.0, 47200.0),
    (75500.0, 81000.0),
    (119980.0, 120020.0),
    (142000.0, 149000.0),
    (241000.0, 250000.0),
]

PROPAGATION_MODES = [
    "",
    "AS",
    "AUE",
    "AUR",
    "BS",
    "ECH",
    "EME",
    "ES",
    "F2",
    "FAI",
    "INTERNET",
    "ION",
    "IRL",
    "MS",
    "RPT",
    "RS",
    "SAT",
    "TEP",
    "TR",
]

ADIF_VERSION = "3.0.4"


class ADIF:

    """The ADIF class supplies methods for reading, parsing, and writing log files in the Amateur Data Interchange Format (ADIF).
    For more information, visit http://adif.org/"""

    def __init__(self):
        """Initialise class for I/O of files using the Amateur Data Interchange Format (ADIF)."""
        return

    def is_valid(self, field_name, data, data_type):
        """Validate the data in a field with respect to the ADIF specification.

        :arg str field_name: The name of the ADIF field.
        :arg str data: The data of the ADIF field to validate.
        :arg str data_type: The type of data to be validated. See http://www.adif.org/304/ADIF_304.htm#Data_Types for the full list with descriptions.
        :returns: True or False to indicate whether the data is valid or not.
        :rtype: bool
        """

        logging.debug(
            "Validating the following data in field '%s': %s" % (field_name, data)
        )

        # Allow an empty string or None, in case the user doesn't want
        # to fill in this field.
        if not data:
            return True

        if data_type == "N":
            # Allow a decimal point before and/or after any numbers,
            # but don't allow a decimal point on its own.
            m = re.match(r"-?(([0-9]+\.?[0-9]*)|([0-9]*\.?[0-9]+))", data)
            if m is None:
                # Did not match anything.
                return False
            else:
                # Make sure we match the whole string,
                # otherwise there may be an invalid character after the match.
                return m.group(0) == data

        elif data_type == "B":
            # Boolean
            m = re.match(r"(Y|N)", data)
            if m is None:
                return False
            else:
                return m.group(0) == data

        elif data_type == "D":
            # Date
            pattern = re.compile(r"([0-9]{4})")
            m_year = pattern.match(data, 0)
            if (m_year is None) or (int(m_year.group(0)) < 1930):
                # Did not match anything.
                return False
            else:
                pattern = re.compile(r"([0-9]{2})")
                m_month = pattern.match(data, 4)
                if (
                    (m_month is None)
                    or int(m_month.group(0)) > 12
                    or int(m_month.group(0)) < 1
                ):
                    # Did not match anything.
                    return False
                else:
                    pattern = re.compile(r"([0-9]{2})")
                    m_day = pattern.match(data, 6)
                    days_in_month = calendar.monthrange(
                        int(m_year.group(0)), int(m_month.group(0))
                    )
                    if (
                        (m_day is None)
                        or int(m_day.group(0)) > days_in_month[1]
                        or int(m_day.group(0)) < 1
                    ):
                        # Did not match anything.
                        return False
                    else:
                        # Make sure we match the whole string,
                        # otherwise there may be an invalid character after the match.
                        return len(data) == 8

        elif data_type == "T":
            # Time
            pattern = re.compile(r"([0-9]{2})")
            m_hour = pattern.match(data, 0)
            if (
                (m_hour is None)
                or (int(m_hour.group(0)) < 0)
                or (int(m_hour.group(0)) > 23)
            ):
                # Did not match anything.
                return False
            else:
                pattern = re.compile(r"([0-9]{2})")
                m_minutes = pattern.match(data, 2)
                if (
                    (m_minutes is None)
                    or int(m_minutes.group(0)) < 0
                    or int(m_minutes.group(0)) > 59
                ):
                    # Did not match anything.
                    return False
                else:
                    if len(data) == 4:
                        # HHMM format
                        return True
                    pattern = re.compile(r"([0-9]{2})")
                    m_seconds = pattern.match(data, 4)
                    if (
                        (m_seconds is None)
                        or int(m_seconds.group(0)) < 0
                        or int(m_seconds.group(0)) > 59
                    ):
                        # Did not match anything.
                        return False
                    else:
                        # Make sure we match the whole string,
                        # otherwise there may be an invalid character after the match.
                        return len(data) == 6  # HHMMSS format

        # FIXME: Need to make sure that the "S" and "M" data types accept ASCII-only characters
        # in the range 32-126 inclusive.
        elif data_type == "S":
            # String
            m = re.match(r"(.+)", data)
            if m is None:
                return False
            else:
                return m.group(0) == data

        elif data_type == "I":
            # IntlString
            m = re.match(r"(.+)", data, re.UNICODE)
            if m is None:
                return False
            else:
                return m.group(0) == data

        elif data_type == "G":
            # IntlMultilineString
            m = re.match(r"(.+(\r\n)*.*)", data, re.UNICODE)
            if m is None:
                return False
            else:
                return m.group(0) == data

        elif data_type == "M":
            # MultilineString
            # m = re.match(r"(.+(\r\n)*.*)", data)
            # if(m is None):
            #   return False
            # else:
            #   return (m.group(0) == data)
            return True

        elif data_type == "L":
            # Location
            pattern = re.compile(r"([EWNS]{1})", re.IGNORECASE)
            m_directional = pattern.match(data, 0)
            if m_directional is None:
                # Did not match anything.
                return False
            else:
                pattern = re.compile(r"([0-9]{3})")
                m_degrees = pattern.match(data, 1)
                if (
                    (m_degrees is None)
                    or int(m_degrees.group(0)) < 0
                    or int(m_degrees.group(0)) > 180
                ):
                    # Did not match anything.
                    return False
                else:
                    pattern = re.compile(r"([0-9]{2}\.[0-9]{3})")
                    m_minutes = pattern.match(data, 4)
                    if (
                        (m_minutes is None)
                        or float(m_minutes.group(0)) < 0
                        or float(m_minutes.group(0)) > 59.999
                    ):
                        # Did not match anything.
                        return False
                    else:
                        # Make sure we match the whole string,
                        # otherwise there may be an invalid character after the match.
                        return len(data) == 10

        elif data_type == "E" or data_type == "A":
            # Enumeration, AwardList.
            if field_name == "MODE":
                return data in list(MODES.keys())
            elif field_name == "SUBMODE":
                submodes = [
                    submode for mode in list(MODES.keys()) for submode in MODES[mode]
                ]
                return data in submodes
            elif field_name == "BAND":
                return data in BANDS
            else:
                return True

        else:
            return True
