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

import logging
import sqlite3 as sqlite

from gi.repository import Gtk

from pyqso.adif import AVAILABLE_FIELD_NAMES_ORDERED


class Log(Gtk.ListStore):

    """A single log inside of the whole logbook. A Log object can store multiple QSOs. This is"""

    def __init__(self, db, name):
        """Set up a new Log object.

        :arg connection: An sqlite database connection.
        :arg str name: The name of the log (i.e. the database table name).
        """
        self.db = db
        self.name = name

        # The ListStore constructor needs to know the data types of the columns.
        # The index is always an integer. We will assume the fields are strings.
        data_types = [int] + [str] * (len(self.db[self.name].columns) - 1)

        # Call the constructor of the super class (Gtk.ListStore).
        Gtk.ListStore.__init__(self, *data_types)

        return

    def populate(self):
        """Remove everything in the Gtk.ListStore that is rendered already (via the TreeView), and start afresh."""

        logging.debug("Populating '%s'..." % self.name)
        self.clear()

        try:
            qsos = self.qsos

            for r in qsos:
                self.append(r.values())
            logging.debug("Finished populating '%s'." % self.name)

        except sqlite.Error as e:
            logging.error(
                "Could not populate '%s' because of a database error." % self.name
            )
            logging.exception(e)

        return

    def add_qso(self, fields_and_data):
        """Add a QSO to the log.

        :arg fields_and_data: A list of dictionaries (or possibly just a single dictionary), with each dictionary representing a single QSO, to be added to the log.
        """

        logging.debug("Adding QSO(s) to log...")


        # TODO: for now we have to .lower() each item bc legacy
        self.db[self.name].insert({k.lower(): v for k, v in fields_and_data.items() if v})
        index = self.db[self.name].insert(fields_and_data)

        # Add the QSOs to the ListStore as well.

        liststore_entry = [index]

        for field_name in self.db[self.name].columns:
            # Ignore the primary key column
            if field_name == "id":
                continue
            # Note: r may contain column names that are not in AVAILABLE_FIELD_NAMES_ORDERED,
            # so we need to loop over and only select those that are, since the ListStore will
            # expect a specific number of columns.
            liststore_entry.append(fields_and_data[field_name.upper()])

        self.append(liststore_entry)

        logging.debug("Successfully added the QSO(s) to the log.")
        return

    def delete_qso(self, index, iter=None):
        """Delete a specified QSO from the log. The corresponding QSO is also deleted from the Gtk.ListStore data structure.

        :arg int index: The index of the QSO in the SQL database.
        :arg iter: The iterator pointing to the QSO to be deleted in the Gtk.ListStore. If the default value of None is used, only the database entry is deleted and the corresponding Gtk.ListStore is left alone.
        :raises sqlite.Error, IndexError: If the QSO could not be deleted.
        """
        logging.debug("Deleting QSO from log...")

        # Delete the selected row in database.
        self.db[self.name].delete(id=index)

        # Delete the selected row in the Gtk.ListStore.
        if iter is not None:
            self.remove(iter)

        logging.debug("Successfully deleted the QSO from the log.")
        return

    def edit_qso(self, index, field_name, data, iter=None, column_index=None):
        """Edit a specified QSO by replacing the current data in a specified field with the data provided.

        :arg int index: The index of the QSO in the SQL database.
        :arg str field_name: The name of the field whose data should be modified.
        :arg str data: The data that should replace the current data in the field.
        :arg iter: The iterator pointing to the QSO to be edited in the Gtk.ListStore. If the default value of None is used, only the database entry is edited and the corresponding Gtk.ListStore is left alone.
        :arg column_index: The index of the column in the Gtk.ListStore to be edited. If the default value of None is used, only the database entry is edited and the corresponding Gtk.ListStore is left alone.
        :raises sqlite.Error, IndexError: If the QSO could not be edited.
        """
        logging.debug("Editing field '%s' in QSO %d..." % (field_name, index))

        #self.db[self.name].update(dict(id=index, field_name)

        #c = self.connection.cursor()
        #query = "UPDATE %s SET %s" % (self.name, field_name)
        #query = query + "=? WHERE id=?"
        #c.execute(query, [data, index])  # First update the SQL database...


        if iter is not None and column_index is not None:
            self.set(iter, column_index, data)  # ...and then the ListStore.
        logging.debug(
            "Successfully edited field '%s' in QSO %d in the log." % (field_name, index)
        )
        return

    def remove_duplicates(self):
        """Remove any duplicate QSOs from the log.

        :returns: The total number of duplicates, and the number of duplicates that were successfully removed. Hopefully these will be the same.
        :rtype: tuple
        """
        duplicates = self.get_duplicates()
        if len(duplicates) == 0:
            return (0, 0)  # Nothing to do here.

        removed = 0  # Count the number of QSOs that are removed. Hopefully this will be the same as len(duplicates).
        iter = self.get_iter_first()  # Start with the first row in the log.
        prev = iter  # Keep track of the previous iter (initially this will be the same as the first row in the log).
        while iter is not None:
            row_index = self.get_value(iter, 0)  # Get the index.
            if row_index in duplicates:  # Is this a duplicate row? If so, delete it.
                self.delete_qso(row_index, iter)
                removed += 1
                iter = prev  # Go back to the iter before the QSO that was just removed and continue from there.
                continue
            prev = iter
            iter = self.iter_next(
                iter
            )  # Move on to the next row, until iter_next returns None.

        return (len(duplicates), removed)

    def rename(self, new_name):
        """Rename the log.

        :arg str new_name: The new name for the log.
        :returns: True if the renaming process is successful. Otherwise returns False.
        :rtype: bool
        """

        """
        try:
            with self.connection:
                # First try to alter the table name in the database.
                c = self.connection.cursor()
                query = "ALTER TABLE %s RENAME TO %s" % (self.name, new_name)
                c.execute(query)
            # If the table name change was successful, then change the name attribute of the Log object too.
            self.name = new_name
            success = True
        except sqlite.Error as e:
            logging.exception(e)
            success = False
        return success
        """

    def get_duplicates(self):
        pass

    def get_qso_by_index(self, index):
        """Return a QSO with a given index in the log.

        :arg int index: The index of the QSO in the SQL database.
        :returns: The desired QSO, represented by a dictionary of field-value pairs.
        :rtype: dict
        :raises sqlite.Error: If the QSO could not be retrieved from the database.
        """
        result = self.db[self.name].find(id=index)
        return result.find_one()

    @property
    def qsos(self):
        """Return a list of all the QSOs in the log.

        :returns: A list of all the QSOs in the log. Each QSO is represented by a dictionary.
        :rtype: dict
        :raises sqlite.Error: If the QSOs could not be retrieved from the database.
        """
        return self.db[self.name].all()

    @property
    def qso_count(self):
        """Return the total number of QSOs in the log.

        :returns: The total number of QSOs in the log.
        :rtype: int
        :raises sqlite.Error: If the QSO count could not be determined due to a database error.
        """
        return self.db[self.name].count()
