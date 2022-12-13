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

from gi.repository import Gtk


class Menu:

    """The menu bar along the top of the main window."""

    def __init__(self, application):
        """Set up all menu items and connect to the various functions.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application
        self.builder = self.application.builder

        # Collect Gtk menu items and connect signals.
        self.items = {}

        # New logbook
        self.items["NEW_LOGBOOK"] = self.builder.get_object("mitem_new_logbook")
        self.items["NEW_LOGBOOK"].connect("activate", self.application.logbook.new)

        # Open logbook
        self.items["OPEN_LOGBOOK"] = self.builder.get_object("mitem_open_logbook")
        self.items["OPEN_LOGBOOK"].connect("activate", self.application.logbook.open)

        # Close logbook
        self.items["CLOSE_LOGBOOK"] = self.builder.get_object("mitem_close_logbook")
        self.items["CLOSE_LOGBOOK"].connect("activate", self.application.logbook.close)

        # New log
        self.items["NEW_LOG"] = self.builder.get_object("mitem_new_log")
        self.items["NEW_LOG"].connect("activate", self.application.logbook.new_log)

        # Delete the current log
        self.items["DELETE_LOG"] = self.builder.get_object("mitem_delete_log")
        self.items["DELETE_LOG"].connect(
            "activate", self.application.logbook.delete_log
        )

        # Rename the current log
        self.items["RENAME_LOG"] = self.builder.get_object("mitem_rename_log")
        self.items["RENAME_LOG"].connect(
            "activate", self.application.logbook.rename_log
        )

        # Export the current log as Cabrillo
        self.items["EXPORT_LOG_CABRILLO"] = self.builder.get_object(
            "mitem_export_log_cabrillo"
        )
        self.items["EXPORT_LOG_CABRILLO"].connect(
            "activate", self.application.logbook.export_log_cabrillo
        )

        # Preferences
        self.items["PREFERENCES"] = self.builder.get_object("mitem_preferences")
        self.items["PREFERENCES"].connect("activate", self.application.show_preferences)

        # Quit
        self.items["QUIT"] = self.builder.get_object("mitem_quit")
        self.items["QUIT"].connect("activate", Gtk.main_quit)

        # Add qso
        self.items["ADD_QSO"] = self.builder.get_object("mitem_add_qso")
        self.items["ADD_QSO"].connect(
            "activate", self.application.logbook.add_qso_callback
        )

        # Edit selected qso
        self.items["EDIT_QSO"] = self.builder.get_object("mitem_edit_qso")
        self.items["EDIT_QSO"].connect(
            "activate", self.application.logbook.edit_qso_callback
        )

        # Delete selected qso
        self.items["DELETE_QSO"] = self.builder.get_object("mitem_delete_qso")
        self.items["DELETE_QSO"].connect(
            "activate", self.application.logbook.delete_qso_callback
        )

        # Remove duplicates
        self.items["REMOVE_DUPLICATES"] = self.builder.get_object(
            "mitem_remove_duplicates"
        )
        self.items["REMOVE_DUPLICATES"].connect(
            "activate", self.application.logbook.remove_duplicates_callback
        )

        # Record count
        self.items["QSO_COUNT"] = self.builder.get_object("mitem_qso_count")
        self.items["QSO_COUNT"].connect(
            "activate", self.application.logbook.qso_count_callback
        )

        # About
        self.items["ABOUT"] = self.builder.get_object("mitem_about")
        self.items["ABOUT"].connect("activate", self.application.show_about)

        self.set_logbook_item_sensitive(True)
        self.set_log_items_sensitive(False)
        self.set_qso_items_sensitive(False)

        return

    def set_logbook_item_sensitive(self, sensitive):
        """Enable/disable logbook-related menu items.

        :arg bool sensitive: If True, enable the 'new logbook' and 'open logbook' menu items. If False, disable them.
        """

        self.items["NEW_LOGBOOK"].set_sensitive(sensitive)
        self.items["OPEN_LOGBOOK"].set_sensitive(sensitive)
        self.items["CLOSE_LOGBOOK"].set_sensitive(not sensitive)
        return

    def set_log_items_sensitive(self, sensitive):
        """Enable/disable log-related menu items.

        :arg bool sensitive: If True, enable all the log-related menu items. If False, disable them all.
        """

        for item_name in [
            "NEW_LOG",
            "DELETE_LOG",
            "RENAME_LOG",
            "EXPORT_LOG_CABRILLO",
        ]:
            self.items[item_name].set_sensitive(sensitive)
        return

    def set_qso_items_sensitive(self, sensitive):
        """Enable/disable qso-related menu items.

        :arg bool sensitive: If True, enable all the QSO-related menu items. If False, disable them all.
        """

        for item_name in [
            "ADD_QSO",
            "EDIT_QSO",
            "DELETE_QSO",
            "REMOVE_DUPLICATES",
            "QSO_COUNT",
        ]:
            self.items[item_name].set_sensitive(sensitive)
        return
