#!/usr/bin/env python3

#    Copyright (C) 2013-2017 Christian Thomas Jacobs.

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


from gi.repository import Gdk, Gtk

import base64
from pyqso import util

from datetime import datetime

from loguru import logger

try:
    import Hamlib

    have_hamlib = True
except ImportError:
    logger.warning("Could not import the Hamlib module!")
    have_hamlib = False

from pyqso import adif, callsign_lookup
from pyqso.calendar_dialog import CalendarDialog
from pyqso.ui.popup_dialog import PopupDialog
from pyqso.ui.form_dialog import FormDialog

class AddQSODialog(FormDialog):

    """A dialog through which users can enter information about a QSO."""

    def __init__(self, application, log, db, index=None):
        """Set up the layout of the QSO dialog, populate the various fields with the QSO details (if the already exists), and show the dialog to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        :arg log: The log to which the qso belongs (or will belong).
        :arg int index: If specified, then the dialog turns into 'edit QSO mode' and fills the data sources (e.g. the Gtk.Entry boxes) with the existing data in the log. If not specified (i.e. index is None), then the dialog starts off with nothing in the data sources.
        """

        super().__init__(application, log, db, index)

        logger.debug("Setting up the QSO dialog...")

        glade_file_path = str(util.get_glade_path())
        self.builder.add_objects_from_file(glade_file_path, ("qso_dialog",))
        self.dialog = self.builder.get_object("qso_dialog")
        self.builder.get_object("qso_dialog").connect(
            "key-press-event", self.on_key_press
        )

        # Set dialog title
        if index is not None:
            self.dialog.set_title("Edit Record %d" % index)
        else:
            self.dialog.set_title("Add Record")

        # Create label:entry pairs and store them in a dictionary
        self.form_data = {}

        # QSO INFORMATION

        # CALL
        self.form_data["call"] = self.builder.get_object("qso_call_entry")
        self.builder.get_object("callsign_lookup").connect(
            "clicked", self.callsign_lookup_callback
        )

        # DATE
        self.form_data["QSO_DATE"] = self.builder.get_object("qso_date_entry")
        self.builder.get_object("select_date").connect(
            "clicked", self.calendar_callback
        )

        # TIME
        self.form_data["TIME_ON"] = self.builder.get_object("qso_time_entry")
        self.builder.get_object("current_datetime").connect(
            "clicked", self.set_current_datetime_callback
        )

        # freq
        self.form_data["freq"] = self.builder.get_object("qso_frequency_entry")
        (section, option) = ("qsos", "default_frequency_unit")
        if self.have_config and self.config.has_option(section, option):
            self.frequency_unit = self.config.get(section, option)
            self.builder.get_object("qso_frequency_label").set_label(
                "Frequency (%s)" % self.frequency_unit
            )
        else:
            self.frequency_unit = "MHz"

        # band
        band_field = self.builder.get_object("band_combo")
        for band in adif.BANDS:
            band_field.append_text(band)
        band_field.set_active(0)  # Set an empty string as the default option.

        # mode
        mode_field = self.builder.get_object("mode_combo")
        for mode in sorted(adif.MODES.keys()):
            mode_field.append_text(mode.lower())

        mode_field.set_active(0)
        mode_field.connect("changed", self.on_mode_changed)

        # SUBMODE
        submode_field = self.builder.get_object("mode_combo")
        submode_field.append_text("")
        submode_field.set_active(0)  # Set an empty string as the default option.

        # PROP_MODE
        prop_mode_field = self.builder.get_object("prop_mode_combo")
        for propagation_mode in adif.PROPAGATION_MODES:
            prop_mode_field.append_text(propagation_mode)
        prop_mode_field.set_active(0)

        # POWER
        #self.form_data["tx_pwr"] = self.builder.get_object("qso_power_entry")

        # RST_SENT
        #self.form_data["RST_SENT"] = self.builder.get_object("qso_rst_sent_entry")

        # RST_RCVD
        #self.form_data["RST_RCVD"] = self.builder.get_object("qso_rst_received_entry")


        # TODO: the dropdown options for the QSL combo boxes should be defined # elswhere

        # QSL_SENT
        qsl_sent_field = self.builder.get_object("qsl_sent_combo")
        qsl_sent_options = ["", "Y", "N", "R", "Q", "I"]
        for option in qsl_sent_options:
            qsl_sent_field.append_text(option)

        qsl_sent_field.set_active(0)

        # TODO: the dropdown options for the QSL combo boxes should be defined # elswhere

        # QSL_RCVD
        qsl_rcvd_field = self.builder.get_object("qsl_rcvd_combo")
        qsl_rcvd_options = ["", "Y", "N", "R", "I", "V"]
        for option in qsl_rcvd_options:
            qsl_rcvd_field.append_text(option)
        qsl_rcvd_field.set_active(0)

        # Populate various fields, if possible.
        if index is not None:
            # If we're editing an existing QSO, display its current data in the input boxes.
            qso = log.get_qso_by_index(index)

            logger.debug(f"qso.items() from QSODialog.add(): {qso.items()}")

            for field, data in qso.items():
                field_entry = f"{field}_entry"

                if not data:
                    continue

                if field == "id":
                    continue
                elif field == "band":
                    # TODO: replace
                    self.set_form_field_text(field_entry, adif.BANDS.index(data))
                elif field == "mode":
                    self.set_form_field_text(field_entry, sorted(adif.MODES.keys()).index(data))
                elif field == "submode":
                    submode = qso.get("submode")
                    if submode:
                        self.set_form_field_text(field_entry, adif.MODES[data].index(data))
                else:
                    self.set_form_field_text(field_entry, data)

        else:
            # Automatically fill in the current date and time
            self.set_current_datetime_callback()

            # Set up default field values
            # Mode
            (section, option) = ("qsos", "default_mode")
            if self.have_config and self.config.has_option(section, option):
                mode = self.config.get(section, option)
            else:
                mode = ""

            # TODO: replace with set_field()
            self.builder.get_object("mode_combo").set_active(sorted(adif.MODES.keys()).index(mode))

            # Submode
            (section, option) = ("qsos", "default_submode")
            if self.have_config and self.config.has_option(section, option):
                submode = self.config.get(section, option)
            else:
                submode = ""

            self.set_form_field_text("submode", adif.MODES[mode].index(submode))

            # Power
            (section, option) = ("qsos", "default_power")
            if self.have_config and self.config.has_option(section, option):
                power = self.config.get(section, option)
            else:
                power = ""

            self.set_form_field_text("tx_pwr", power)

            # If the Hamlib module is present, then use it to fill in various fields if desired.
            if have_hamlib:
                if (
                    self.have_config
                    and self.config.has_option("hamlib", "autofill")
                    and self.config.has_option("hamlib", "rig_model")
                    and self.config.has_option("hamlib", "rig_pathname")
                ):
                    autofill = self.config.getboolean("hamlib", "autofill")
                    rig_model = self.config.get("hamlib", "rig_model")
                    rig_pathname = self.config.get("hamlib", "rig_pathname")
                    if autofill:
                        self.hamlib_autofill(rig_model, rig_pathname)

        # Do we want PyQSO to autocomplete the Band field based on the Frequency field?

        # TODO: refactor
        (section, option) = ("qsos", "autocomplete_band")
        if self.have_config and self.config.has_option(section, option):
            autocomplete_band = self.config.getboolean(section, option)
            if autocomplete_band:
                self.builder.get_object("freq_entry").connect("changed", self.autocomplete_band)
        else:
            # If no configuration file exists, autocomplete the Band field by default.
            self.builder.get_object("freq_entry").connect("changed", self.autocomplete_band)

        self.dialog.show_all()

        logger.debug("Record dialog ready!")

        return

    def on_mode_changed(self, combo):
        """If the mode field has changed its value, then fill the submode field with all the available submode options for that new MODE."""
        self.form_data["submode"].get_model().clear()
        mode = combo.get_active_text()
        for submode in adif.MODES[mode]:
            self.form_data["submode"].append_text(submode)
        self.form_data["submode"].set_active(
            adif.MODES[mode].index("")
        )  # Set the submode to an empty string.
        return

    def on_key_press(self, widget, event):
        """If the Return key is pressed, emit the "OK" response to record the QSO."""
        child = widget.get_focus()
        if (
            not (
                isinstance(child, Gtk.ToggleButton)
                or isinstance(child, Gtk.Button)
                or isinstance(child, Gtk.TextView)
            )
            and event.keyval == Gdk.KEY_Return
        ):
            self.dialog.emit("response", Gtk.ResponseType.OK)
        return

    def autocomplete_band(self, widget=None):
        """If a value for the Frequency is entered, this function autocompletes the Band field."""

        frequency = self.get_form_field_text("freq")

        # Check whether we actually have a (valid) value to use. If not, set the BAND field to an empty string ("").
        try:
            frequency = float(frequency)
        except ValueError:
            self.set_form_field_text("band", 0)
            return

        # Convert to MHz if necessary.
        if self.frequency_unit != "MHz":
            frequency = self.convert_frequency(
                frequency, from_unit=self.frequency_unit, to_unit="MHz"
            )

        band = util.guess_frequency_band(frequency)

        if band:
            logger.debug(f"Frequency given is {frequency}, band guess is {band}.  Setting text")
            self.set_form_field_text("band", band)
        else:
            logger.debug(f"Frequency given is {frequency}, could not guess band. Setting text to empty")
            self.set_form_field_text("band", 0)
        return

    def hamlib_autofill(self, rig_model, rig_pathname):
        """Set the various fields using data from the radio via Hamlib.

        :arg str rig_model: The model of the radio/rig.
        :arg str rig_pathname: The path to the rig (or rig control device).
        """

        # Open a communication channel to the radio.
        try:
            Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)
            rig = Hamlib.Rig(
                Hamlib.__dict__[rig_model]
            )  # Look up the model's numerical index in Hamlib's symbol dictionary.
            rig.set_conf("rig_pathname", rig_pathname)
            rig.open()
        # TODO: do not use bare 'except'
        except:
            logger.error(
                "Could not open a communication channel to the rig via Hamlib!"
            )
            return

        # Frequency
        try:
            frequency = "%.6f" % (rig.get_freq() / 1.0e6)  # Converting to MHz here.
            # Convert to the desired unit, if necessary.
            if self.frequency_unit != "MHz":
                frequency = str(
                    self.convert_frequency(
                        frequency, from_unit="MHz", to_unit=self.frequency_unit
                    )
                )
            self.set_form_field_text("freq", frequency)
        # TODO: do not use bare 'except'
        except:
            logger.error("Could not obtain the current frequency via Hamlib!")

        # Mode
        try:
            (mode, width) = rig.get_mode()
            mode = Hamlib.rig_strrmode(mode).upper()
            # Handle USB and LSB as special cases.
            if mode == "USB" or mode == "LSB":
                submode = mode
                mode = "SSB"
                self.form_data["mode"].set_active(sorted(adif.MODES.keys()).index(mode))
                self.form_data["submode"].set_active(adif.MODES[mode].index(submode))
            else:
                self.form_data["mode"].set_active(sorted(adif.MODES.keys()).index(mode))
        # TODO: do not use bare 'except'
        except:
            logger.error(
                "Could not obtain the current mode (e.g. FM, AM, CW) via Hamlib!"
            )

        # Close communication channel.
        try:
            rig.close()
        # TODO: do not use bare 'except'
        except:
            logger.error(
                "Could not close the communication channel to the rig via Hamlib!"
            )

        return

    def callsign_lookup_callback(self, widget=None):
        """Get the callsign-related data from an online database and store it in the relevant Gtk.Entry boxes, but return None."""

        try:
            if self.have_config and self.config.has_option("qsos", "callsign_database"):
                database = self.config.get("qsos", "callsign_database")
                if database == "":
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            d = PopupDialog(
                parent=self.dialog,
                message="To perform a callsign lookup, please specify the name of the callsign database in the Preferences.",
            )
            d.error()
            return

        try:
            if database == "qrz.com":
                # QRZ.com
                lookup = callsign_lookup.CallsignLookupQRZ(parent=self.dialog)
            else:
                raise ValueError("Unknown callsign database: %s" % database)
        except ValueError as e:
            logger.exception(e)
            d = PopupDialog(parent=self.dialog, message=e)
            d.error()
            return

        # Get username and password from configuration file.
        if (
            self.have_config
            and self.config.has_option("qsos", "callsign_database_username")
            and self.config.has_option("qsos", "callsign_database_password")
        ):
            username = self.config.get("qsos", "callsign_database_username")
            password = base64.b64decode(
                self.config.get("qsos", "callsign_database_password")
            ).decode("utf-8")
            if not username or not password:
                details_given = False
            else:
                details_given = True
        else:
            details_given = False
        if not details_given:
            d = PopupDialog(
                parent=self.dialog,
                message="To perform a callsign lookup, please specify your username and password in the Preferences.",
            )
            d.error()
            return

        # Get the callsign from the CALL field.
        full_callsign = self.form_data["call"].get_text()
        if not full_callsign:
            # Empty callsign field.
            d = PopupDialog(
                parent=self.dialog, message="Please enter a callsign to lookup."
            )
            d.error()
            return

        # Connect to the database.
        connected = lookup.connect(username, password)
        if connected:
            # Check whether we want to ignore any prefixes (e.g. "IA/") or suffixes "(e.g. "/M") in the callsign
            # before performing the lookup.
            if self.have_config and self.config.has_option("qsos", "ignore_prefix_suffix"):
                ignore_prefix_suffix = self.config.getboolean("qsos", "ignore_prefix_suffix")
            else:
                ignore_prefix_suffix = True

            # Perform the lookup.
            fields_and_data = lookup.lookup(
                full_callsign, ignore_prefix_suffix=ignore_prefix_suffix
            )
            for field_name in list(fields_and_data.keys()):
                self.set_form_field_text(field_name, fields_and_data[field_name])
        return

    def calendar_callback(self, widget):
        """Open up a calendar widget for easy QSO_DATE selection. Return None after the user destroys the dialog."""
        c = CalendarDialog(self.application)
        response = c.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.set_form_field_text("date", c.date)
        c.dialog.destroy()
        return


    def set_current_datetime_callback(self, widget=None):
        """Insert the current date and time."""

        # Do we want to use UTC or the computer's local time?
        (section, option) = ("qsos", "use_utc")
        if self.have_config and self.config.has_option(section, option):
            use_utc = self.config.getboolean(section, option)
            if use_utc:
                dt = datetime.utcnow()
            else:
                dt = datetime.now()
        else:
            dt = (
                datetime.utcnow()
            )  # Use UTC by default, since this is expected by ADIF.

        self.set_form_field_text("date", dt.strftime("%Y%m%d"))
        self.set_form_field_text("time", dt.strftime("%H%M"))

        return

    def convert_frequency(self, frequency, from_unit, to_unit):
        """Convert a frequency from one unit to another.

        :arg float frequency: The frequency to convert.
        :arg str from_unit: The current unit of the frequency.
        :arg str to_unit: The desired unit of the frequency.
        :rtype: float
        :returns: The frequency in the to_unit.
        """
        scaling = {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
        # Check that the from/to frequency units are valid.
        try:
            if from_unit not in scaling.keys():
                raise ValueError("Unknown frequency unit '%s' in from_unit" % from_unit)
            if to_unit not in scaling.keys():
                raise ValueError("Unknown frequency unit '%s' in to_unit" % to_unit)
        except ValueError as e:
            logger.exception(e)
            return frequency
        # Cast to float before scaling.
        if not isinstance(frequency, float):
            try:
                if frequency == "" or frequency is None:
                    return frequency
                else:
                    frequency = float(frequency)
            except (ValueError, TypeError):
                logger.exception(
                    "Could not convert frequency to a floating-point value."
                )
                return frequency
        # Do not bother scaling if the units are the same.
        if from_unit == to_unit:
            return frequency

        coefficient = scaling[from_unit] / scaling[to_unit]
        return float("%.6f" % (coefficient * frequency))


