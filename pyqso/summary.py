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
from os.path import basename, getmtime

from gi.repository import Gtk

from pyqso import util


class Summary(object):
    def __init__(self, application):
        """Create a summary page containing various statistics such as the number of logs in the logbook, the logbook's modification date, etc.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        self.application = application
        self.logbook = self.application.logbook
        self.builder = self.application.builder

        glade_file_path = util.get_glade_path()
        self.builder.add_objects_from_file(str(glade_file_path), ("summary_page",))
        self.summary_page = self.builder.get_object("summary_page")

        self.items = {}

        # Database name in large font at the top of the summary page
        self.builder.get_object("database_name").set_markup(
            '<span size="x-large">%s</span>' % basename(self.logbook.path)
        )
        self.items["LOG_COUNT"] = self.builder.get_object("log_count")
        self.items["QSO_COUNT"] = self.builder.get_object("qso_count")
        self.items["DATE_MODIFIED"] = self.builder.get_object("date_modified")

        # Summary tab label and icon.
        tab = Gtk.Box(homogeneous=False, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        label = Gtk.Label(label="Summary  ")
        icon = Gtk.Image.new_from_icon_name(Gtk.STOCK_INDEX, Gtk.IconSize.MENU)
        tab.pack_start(label, False, False, 0)
        tab.pack_start(icon, False, False, 0)
        tab.show_all()

        self.logbook.notebook.insert_page(
            self.summary_page, tab, 0
        )  # Append as a new tab
        self.logbook.notebook.show_all()

        return

    def update(self):
        """Update the information presented on the summary page."""

        self.items["LOG_COUNT"].set_label(str(self.logbook.log_count))
        self.items["QSO_COUNT"].set_label(str(self.logbook.qso_count))
        try:
            t = datetime.fromtimestamp(getmtime(self.logbook.path)).strftime(
                "%d %B %Y @ %H:%M"
            )
            self.items["DATE_MODIFIED"].set_label(str(t))
        except (IOError, OSError) as e:
            logging.exception(e)
        return
