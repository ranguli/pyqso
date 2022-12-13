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

from gi.repository import Gtk
import logging

import configparser
import os.path
import base64

try:
    import Hamlib

    have_hamlib = True
except ImportError:
    logging.warning("Could not import the Hamlib module!")
    have_hamlib = False

from pyqso.adif import AVAILABLE_FIELD_NAMES_ORDERED, MODES

PREFERENCES_FILE = os.path.expanduser("~/.config/pyqso/preferences.ini")


class PreferencesDialog:

    """A dialog to specify the PyQSO preferences."""

    def __init__(self, application):
        """Set up the various pages of the preferences dialog.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        logging.debug("Setting up the preferences dialog...")

        self.application = application
        self.builder = self.application.builder
        glade_file_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)), "res", "pyqso.glade"
        )
        self.builder.add_objects_from_file(glade_file_path, ("preferences_dialog",))
        self.dialog = self.builder.get_object("preferences_dialog")

        self.general = GeneralPage(self.dialog, self.builder)
        self.view = ViewPage(self.dialog, self.builder)
        self.qsos = RecordsPage(self.dialog, self.builder)
        self.import_export = ImportExportPage(self.dialog, self.builder)
        self.hamlib = HamlibPage(self.dialog, self.builder)

        self.dialog.show_all()

        logging.debug("Preferences dialog ready!")

        return

    def commit(self):
        """Commit the user preferences to the configuration file."""

        logging.debug("Committing the user preferences to the configuration file...")

        config = configparser.ConfigParser()

        # General
        config.add_section("general")
        for key in list(self.general.data.keys()):
            config.set("general", key.lower(), str(self.general.data[key]))

        # View
        config.add_section("view")
        for key in list(self.view.data.keys()):
            config.set("view", key.lower(), str(self.view.data[key]))

        # Records
        config.add_section("qsos")
        for key in list(self.qsos.data.keys()):
            config.set("qsos", key.lower(), str(self.qsos.data[key]))

        # Import/Export
        config.add_section("import_export")
        for key in list(self.import_export.data.keys()):
            config.set("import_export", key.lower(), str(self.import_export.data[key]))

        # Hamlib
        config.add_section("hamlib")
        for key in list(self.hamlib.data.keys()):
            config.set("hamlib", key.lower(), str(self.hamlib.data[key]))

        # Write the preferences to file.
        with open(os.path.expanduser(PREFERENCES_FILE), "w") as f:
            config.write(f)

        return


class GeneralPage:

    """The section of the preferences dialog containing general preferences."""

    def __init__(self, parent, builder):
        """Set up the General page of the Preferences dialog."""

        self.parent = parent
        self.builder = builder
        self.sources = {}

        # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
        # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
        config = configparser.ConfigParser()
        have_config = config.read(PREFERENCES_FILE) != []

        # Show statistics.
        self.sources["SHOW_YEARLY_STATISTICS"] = self.builder.get_object(
            "general_show_yearly_statistics_checkbutton"
        )
        (section, option) = ("general", "show_yearly_statistics")
        if have_config and config.has_option(section, option):
            self.sources["SHOW_YEARLY_STATISTICS"].set_active(
                config.getboolean(section, option)
            )
        else:
            self.sources["SHOW_YEARLY_STATISTICS"].set_active(False)

        # Default logbook.
        self.sources["DEFAULT_LOGBOOK"] = self.builder.get_object(
            "general_default_logbook_checkbutton"
        )
        (section, option) = ("general", "default_logbook")
        if have_config and config.has_option(section, option):
            self.sources["DEFAULT_LOGBOOK"].set_active(
                config.getboolean(section, option)
            )
        else:
            self.sources["DEFAULT_LOGBOOK"].set_active(False)
        self.sources["DEFAULT_LOGBOOK"].connect(
            "toggled", self.on_default_logbook_toggled
        )

        self.sources["DEFAULT_LOGBOOK_PATH"] = self.builder.get_object(
            "general_default_logbook_entry"
        )
        (section, option) = ("general", "default_logbook")
        # Disable the text entry box if the default logbook checkbox is not checked.
        if have_config and config.has_option(section, option):
            self.sources["DEFAULT_LOGBOOK_PATH"].set_sensitive(
                self.sources["DEFAULT_LOGBOOK"].get_active()
            )
            self.builder.get_object("general_default_logbook_button").set_sensitive(
                self.sources["DEFAULT_LOGBOOK"].get_active()
            )
        else:
            self.sources["DEFAULT_LOGBOOK_PATH"].set_sensitive(False)
            self.builder.get_object("general_default_logbook_button").set_sensitive(
                False
            )
        (section, option) = ("general", "default_logbook_path")
        if have_config and config.has_option(section, option):
            self.sources["DEFAULT_LOGBOOK_PATH"].set_text(config.get(section, option))

        self.builder.get_object("general_default_logbook_button").connect(
            "clicked", self.on_default_logbook_clicked
        )

        # Keep 'Add Record' dialog open.
        self.sources["KEEP_OPEN"] = self.builder.get_object(
            "general_keep_open_checkbutton"
        )
        (section, option) = ("general", "keep_open")
        if have_config and config.has_option(section, option):
            self.sources["KEEP_OPEN"].set_active(config.getboolean(section, option))
        else:
            self.sources["KEEP_OPEN"].set_active(False)

        return

    @property
    def data(self):
        """User preferences regarding General settings."""
        data = {}
        data["SHOW_TOOLBOX"] = self.sources["SHOW_TOOLBOX"].get_active()
        data["SHOW_YEARLY_STATISTICS"] = self.sources[
            "SHOW_YEARLY_STATISTICS"
        ].get_active()
        data["DEFAULT_LOGBOOK"] = self.sources["DEFAULT_LOGBOOK"].get_active()
        data["DEFAULT_LOGBOOK_PATH"] = os.path.expanduser(
            self.sources["DEFAULT_LOGBOOK_PATH"].get_text()
        )
        data["KEEP_OPEN"] = self.sources["KEEP_OPEN"].get_active()
        return data

    def on_default_logbook_toggled(self, widget, data=None):
        if widget.get_active():
            self.sources["DEFAULT_LOGBOOK_PATH"].set_sensitive(True)
            self.builder.get_object("general_default_logbook_button").set_sensitive(
                True
            )
        else:
            self.sources["DEFAULT_LOGBOOK_PATH"].set_sensitive(False)
            self.builder.get_object("general_default_logbook_button").set_sensitive(
                False
            )
        return

    def on_default_logbook_clicked(self, widget):
        """Let the user select the default logbook file via a file chooser dialog,
        and set the path in the adjacent entry box."""

        dialog = Gtk.FileChooserDialog(
            "Select SQLite Database File",
            self.parent,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self.sources["DEFAULT_LOGBOOK_PATH"].set_text(path)
        dialog.destroy()
        return


class ViewPage:

    """The section of the preferences dialog containing view-related preferences."""

    def __init__(self, parent, builder):
        """Set up the View page of the Preferences dialog."""

        self.parent = parent
        self.builder = builder
        self.sources = {}

        config = configparser.ConfigParser()
        have_config = config.read(PREFERENCES_FILE) != []

        # Visible fields
        for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
            self.sources[field_name] = self.builder.get_object(
                "visible_fields_%s" % (field_name.lower())
            )
            if have_config and config.has_option("view", field_name.lower()):
                self.sources[field_name].set_active(
                    config.getboolean("view", field_name.lower())
                )
            else:
                self.sources[field_name].set_active(True)

        return

    @property
    def data(self):
        """User preferences regarding View settings."""
        data = {}
        for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
            data[field_name] = self.sources[field_name].get_active()
        return data


class RecordsPage:

    """The section of the preferences dialog containing QSO-related preferences."""

    def __init__(self, parent, builder):
        """Set up the Record page of the Preferences dialog."""

        self.parent = parent
        self.builder = builder
        self.sources = {}

        # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
        # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
        config = configparser.ConfigParser()
        have_config = config.read(PREFERENCES_FILE) != []

        # Autocomplete
        self.sources["AUTOCOMPLETE_BAND"] = self.builder.get_object(
            "qsos_autocomplete_band_checkbutton"
        )
        (section, option) = ("qsos", "autocomplete_band")
        if have_config and config.has_option(section, option):
            self.sources["AUTOCOMPLETE_BAND"].set_active(
                config.getboolean(section, option)
            )
        else:
            self.sources["AUTOCOMPLETE_BAND"].set_active(True)

        self.sources["USE_UTC"] = self.builder.get_object(
            "qsos_autocomplete_utc_checkbutton"
        )
        (section, option) = ("qsos", "use_utc")
        if have_config and config.has_option(section, option):
            self.sources["USE_UTC"].set_active(config.getboolean(section, option))
        else:
            self.sources["USE_UTC"].set_active(True)

        # Default values

        # Mode
        self.sources["DEFAULT_MODE"] = self.builder.get_object(
            "default_values_mode_combo"
        )
        for mode in sorted(MODES.keys()):
            self.sources["DEFAULT_MODE"].append_text(mode)
        (section, option) = ("qsos", "default_mode")
        if have_config and config.has_option(section, option):
            mode = config.get(section, option)
        else:
            mode = ""
        self.sources["DEFAULT_MODE"].set_active(sorted(MODES.keys()).index(mode))
        self.sources["DEFAULT_MODE"].connect("changed", self.on_mode_changed)

        # Submode
        self.sources["DEFAULT_SUBMODE"] = self.builder.get_object(
            "default_values_submode_combo"
        )
        for submode in MODES[mode]:
            self.sources["DEFAULT_SUBMODE"].append_text(submode)
        (section, option) = ("qsos", "default_submode")
        if have_config and config.has_option(section, option):
            submode = config.get(section, option)
        else:
            submode = ""
        self.sources["DEFAULT_SUBMODE"].set_active(MODES[mode].index(submode))

        # Power
        self.sources["DEFAULT_POWER"] = self.builder.get_object(
            "default_values_tx_power_entry"
        )
        (section, option) = ("qsos", "default_power")
        if have_config and config.has_option(section, option):
            self.sources["DEFAULT_POWER"].set_text(config.get(section, option))
        else:
            self.sources["DEFAULT_POWER"].set_text("")

        # Frequency unit
        self.sources["DEFAULT_FREQUENCY_UNIT"] = self.builder.get_object(
            "default_values_frequency_unit_combo"
        )
        units = ["Hz", "kHz", "MHz", "GHz"]
        for unit in units:
            self.sources["DEFAULT_FREQUENCY_UNIT"].append_text(unit)
        (section, option) = ("qsos", "default_frequency_unit")
        if have_config and config.has_option(section, option):
            self.sources["DEFAULT_FREQUENCY_UNIT"].set_active(
                units.index(config.get(section, option))
            )
        else:
            self.sources["DEFAULT_FREQUENCY_UNIT"].set_active(units.index("MHz"))

        # Callsign lookup
        self.sources["CALLSIGN_DATABASE"] = self.builder.get_object(
            "callsign_lookup_database_combo"
        )
        callsign_database = ["", "qrz.com", "hamqth.com"]
        for database in callsign_database:
            self.sources["CALLSIGN_DATABASE"].append_text(database)
        (section, option) = ("qsos", "callsign_database")
        if have_config and config.has_option(section, option):
            self.sources["CALLSIGN_DATABASE"].set_active(
                callsign_database.index(config.get(section, option))
            )
        else:
            self.sources["CALLSIGN_DATABASE"].set_active(callsign_database.index(""))

        # Login details
        self.sources["CALLSIGN_DATABASE_USERNAME"] = self.builder.get_object(
            "callsign_lookup_login_details_username_entry"
        )
        (section, option) = ("qsos", "callsign_database_username")
        if have_config and config.has_option(section, option):
            self.sources["CALLSIGN_DATABASE_USERNAME"].set_text(
                config.get(section, option)
            )

        self.sources["CALLSIGN_DATABASE_PASSWORD"] = self.builder.get_object(
            "callsign_lookup_login_details_password_entry"
        )
        (section, option) = ("qsos", "callsign_database_password")
        if have_config and config.has_option(section, option):
            password = base64.b64decode(config.get(section, option)).decode("utf-8")
            self.sources["CALLSIGN_DATABASE_PASSWORD"].set_text(password)

        self.sources["IGNORE_PREFIX_SUFFIX"] = self.builder.get_object(
            "callsign_lookup_ignore_prefix_suffix_checkbutton"
        )
        (section, option) = ("qsos", "ignore_prefix_suffix")
        if have_config and config.has_option(section, option):
            self.sources["IGNORE_PREFIX_SUFFIX"].set_active(
                config.getboolean(section, option)
            )
        else:
            self.sources["IGNORE_PREFIX_SUFFIX"].set_active(True)

        return

    @property
    def data(self):
        """User preferences regarding Records settings."""
        data = {}
        data["AUTOCOMPLETE_BAND"] = self.sources["AUTOCOMPLETE_BAND"].get_active()
        data["USE_UTC"] = self.sources["USE_UTC"].get_active()

        data["DEFAULT_MODE"] = self.sources["DEFAULT_MODE"].get_active_text()
        data["DEFAULT_SUBMODE"] = self.sources["DEFAULT_SUBMODE"].get_active_text()
        data["DEFAULT_POWER"] = self.sources["DEFAULT_POWER"].get_text()
        data["DEFAULT_FREQUENCY_UNIT"] = self.sources[
            "DEFAULT_FREQUENCY_UNIT"
        ].get_active_text()

        data["CALLSIGN_DATABASE"] = self.sources["CALLSIGN_DATABASE"].get_active_text()
        data["CALLSIGN_DATABASE_USERNAME"] = self.sources[
            "CALLSIGN_DATABASE_USERNAME"
        ].get_text()
        data["CALLSIGN_DATABASE_PASSWORD"] = base64.b64encode(
            self.sources["CALLSIGN_DATABASE_PASSWORD"].get_text().encode("utf-8")
        ).decode(
            "utf-8"
        )  # Need to convert from bytes to str here.
        data["IGNORE_PREFIX_SUFFIX"] = self.sources["IGNORE_PREFIX_SUFFIX"].get_active()
        return data

    def on_mode_changed(self, combo):
        """If the MODE field has changed its value, then fill the SUBMODE field with all the available SUBMODE options for that new MODE."""
        self.sources["DEFAULT_SUBMODE"].get_model().clear()
        mode = combo.get_active_text()
        for submode in MODES[mode]:
            self.sources["DEFAULT_SUBMODE"].append_text(submode)
        self.sources["DEFAULT_SUBMODE"].set_active(MODES[mode].index(""))
        return


class ImportExportPage:

    """The section of the preferences dialog containing import/export-related preferences."""

    def __init__(self, parent, builder):
        """Set up the Import/Export page of the Preferences dialog."""

        self.parent = parent
        self.builder = builder
        self.sources = {}

        # Remember that the have_config conditional in the PyQSO class may be out-of-date the next time the user opens up the preferences dialog
        # because a configuration file may have been created after launching the application. Let's check to see if one exists again...
        config = configparser.ConfigParser()
        have_config = config.read(PREFERENCES_FILE) != []

        # Import
        self.sources["MERGE_COMMENT"] = self.builder.get_object(
            "adif_import_merge_comment_checkbutton"
        )
        (section, option) = ("import_export", "merge_comment")
        if have_config and config.has_option(section, option):
            self.sources["MERGE_COMMENT"].set_active(config.getboolean(section, option))
        else:
            self.sources["MERGE_COMMENT"].set_active(False)

        return

    @property
    def data(self):
        """User preferences regarding Import/Export settings."""
        data = {}
        data["MERGE_COMMENT"] = self.sources["MERGE_COMMENT"].get_active()
        return data


class HamlibPage:

    """The section of the preferences dialog containing Hamlib-related preferences."""

    def __init__(self, parent, builder):
        """Set up the Hamlib page of the Preferences dialog."""

        self.parent = parent
        self.builder = builder
        self.sources = {}

        config = configparser.ConfigParser()
        have_config = config.read(PREFERENCES_FILE) != []

        self.sources["AUTOFILL"] = self.builder.get_object("hamlib_support_checkbutton")
        (section, option) = ("hamlib", "autofill")
        if have_config and config.has_option(section, option):
            self.sources["AUTOFILL"].set_active(config.getboolean(section, option))
        else:
            self.sources["AUTOFILL"].set_active(False)

        # Get the list of rig models
        models = ["RIG_MODEL_NONE"]
        if have_hamlib:
            try:
                for item in dir(Hamlib):
                    if item.startswith("RIG_MODEL_"):
                        models.append(item)
            # TODO: do not use bare 'except'
            except:
                logging.error("Could not obtain rig models list via Hamlib!")
        else:
            logging.debug(
                "Hamlib module not present. Could not obtain a list of rig models."
            )

        self.sources["RIG_MODEL"] = self.builder.get_object(
            "hamlib_support_model_combo"
        )
        for model in models:
            self.sources["RIG_MODEL"].append_text(model)
        (section, option) = ("hamlib", "rig_model")
        if have_config and config.has_option("hamlib", "rig_model"):
            self.sources["RIG_MODEL"].set_active(
                models.index(config.get("hamlib", "rig_model"))
            )
        else:
            self.sources["RIG_MODEL"].set_active(
                models.index("RIG_MODEL_NONE")
            )  # Set to RIG_MODEL_NONE as the default option.

        # Path to rig
        self.sources["RIG_PATHNAME"] = self.builder.get_object(
            "hamlib_support_path_entry"
        )
        (section, option) = ("hamlib", "rig_pathname")
        if have_config and config.has_option(section, option):
            self.sources["RIG_PATHNAME"].set_text(config.get(section, option))

        return

    @property
    def data(self):
        """User preferences regarding Hamlib settings."""
        data = {}
        data["AUTOFILL"] = self.sources["AUTOFILL"].get_active()
        data["RIG_PATHNAME"] = self.sources["RIG_PATHNAME"].get_text()
        data["RIG_MODEL"] = self.sources["RIG_MODEL"].get_active_text()
        return data
