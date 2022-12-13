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

from pyqso.contest import CONTESTS
from pyqso import util
from cabrillo import data as cabrillo_data


class CabrilloExportDialog:

    """A handler for the Gtk.Dialog through which a user can specify Cabrillo log details."""

    def __init__(self, application):
        """Create and show the Cabrillo export dialog to the user.

        :arg application: The PyQSO application containing the main Gtk window, etc.
        """

        logging.debug("Building new Cabrillo export dialog...")

        self.builder = application.builder

        glade_file_path = str(util.get_glade_path())

        self.glade_prefix = "cabrillo_export"
        self.builder.add_objects_from_file(glade_file_path, (f"{self.glade_prefix}_dialog",))
        self.dialog = self.builder.get_object(f"{self.glade_prefix}_dialog")

        self.population_data = {
            "contest": cabrillo_data.CONTEST,
            "category_power": cabrillo_data.CATEGORY_POWER,
            "category_band": cabrillo_data.CATEGORY_BAND,
            "category_mode": cabrillo_data.CATEGORY_MODE,
            "category_station": cabrillo_data.CATEGORY_STATION,
            "category_operator": cabrillo_data.CATEGORY_OPERATOR,
            "category_transmitter": cabrillo_data.CATEGORY_TRANSMITTER,
            "category_assisted": cabrillo_data.CATEGORY_ASSISTED,
            "category_overlay": cabrillo_data.CATEGORY_OVERLAY,
            "category_time": cabrillo_data.CATEGORY_TIME
        }

        self.__populate_form_fields(self.population_data)

        self.dialog.show_all()

        logging.debug("Cabrillo export dialog built.")

        return

    def __populate_form_fields(self, population_data):
        for k, v in population_data.items():
            gtk_object_path = f"{self.glade_prefix}_{k}_combo"
            gtk_object = self.builder.get_object(gtk_object_path)
            print(gtk_object_path)
            print(gtk_object)
            field = self.builder.get_object(f"{self.glade_prefix}_{k}_combo")
            print(field)
            for dropdown_option in v:
                field.append_text(dropdown_option)

    def get_form_fields(self):
        fields = {field: self.get_form_field(field) for (field) in self.population_data.keys()}
        fields.update({"callsign": self.get_form_field("callsign")})
        fields.update({"myqth": self.get_form_field("myqth")})

        return fields

    def get_form_field(self, field):
        non_combo_fields = [
            "callsign",
            "myqth"
        ]

        if field in non_combo_fields:
            return self.builder.get_object(f"{self.glade_prefix}_{field}_entry").get_text()

        return self.builder.get_object(f"{self.glade_prefix}_{field}_combo").get_active_text()

    @property
    def contest(self):
        """Return the name of the contest.

        :returns: The name of the contest.
        :rtype: str
        """
        self.mycall_entry = self.builder.get_object("cabrillo_export_contest_combo").get_active_text()
        return self.contest_combo.get_active_text()

    @property
    def mycall(self):
        """Return the callsign used during the contest.

        :returns: The callsign used during the contest.
        :rtype: str
        """
        # Always show the callsigns in upper case.
        return self.mycall_entry.get_text().upper()
