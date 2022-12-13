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

from pyqso.adif import AVAILABLE_FIELD_NAMES_ORDERED
from pyqso.log import sqlite, Log


class TestLog(unittest.TestCase):

    """The unit tests for the Log class."""

    def setUp(self):
        """Create a connection to a temporary database and set up the objects needed for the unit tests."""
        self.connection = sqlite.connect(":memory:")
        self.connection.row_factory = sqlite.Row

        self.field_names = [
            "CALL",
            "QSO_DATE",
            "TIME_ON",
            "FREQ",
            "BAND",
            "MODE",
            "RST_SENT",
            "RST_RCVD",
        ]
        self.fields_and_data = {
            "CALL": "TEST123",
            "QSO_DATE": "20130312",
            "TIME_ON": "1234",
            "FREQ": "145.500",
            "BAND": "2m",
            "MODE": "FM",
            "RST_SENT": "59",
            "RST_RCVD": "59",
        }

        c = self.connection.cursor()
        query = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT"
        for field_name in self.field_names:
            s = ", %s TEXT" % field_name.lower()
            query = query + s
        query = query + ")"
        c.execute(query)

        self.log = Log(self.connection, "test")

    def tearDown(self):
        """Destroy the connection to the temporary database."""
        self.connection.close()

    def test_add_missing_db_columns(self):
        """Check that any missing columns in the database are added successfully."""

        c = self.connection.cursor()

        # 'Before' state.
        column_names_before = []
        c.execute("PRAGMA table_info(test)")
        result = c.fetchall()
        for t in result:
            column_names_before.append(t[1].upper())

        # Add missing columns.
        self.log.add_missing_db_columns()

        # 'After' state.
        column_names_after = []
        c.execute("PRAGMA table_info(test)")
        result = c.fetchall()
        for t in result:
            column_names_after.append(t[1].upper())

        print("Column names before: ", column_names_before)
        print("Column names after: ", column_names_after)

        assert (
            len(column_names_before) == len(self.field_names) + 1
        )  # Added 1 here because of the "id" column in all database tables.
        assert len(column_names_after) == len(AVAILABLE_FIELD_NAMES_ORDERED) + 1
        for field_name in AVAILABLE_FIELD_NAMES_ORDERED:
            assert field_name in column_names_after

    def test_add_qso(self):
        """Check that a single qso can be successfully added."""

        self.log.add_qso(self.fields_and_data)

        c = self.connection.cursor()
        c.execute("SELECT * FROM test")
        qsos = c.fetchall()
        assert len(qsos) == 1

        # Check that all the data has been added to all the fields.
        for field_name in self.field_names:
            print(self.fields_and_data[field_name], qsos[0][field_name])
            assert self.fields_and_data[field_name] == qsos[0][field_name]

        # Check consistency of index between Gtk.ListStore and the database.
        assert qsos[0]["id"] == 1
        iter = self.log.get_iter_first()
        row_index = self.log.get_value(iter, 0)
        assert qsos[0]["id"] == row_index

    def test_add_qso_multiple(self):
        """Check that multiple qsos can be successfully added in one go."""
        self.log.add_qso([self.fields_and_data] * 5)

        c = self.connection.cursor()
        c.execute("SELECT * FROM test")
        qsos = c.fetchall()
        assert len(qsos) == 5

    def test_delete_qso(self):
        """Check that a qso can be successfully deleted."""
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )

        c.execute("SELECT * FROM test")
        qsos_before = c.fetchall()

        self.log.delete_qso(1)

        c.execute("SELECT * FROM test")
        qsos_after = c.fetchall()

        assert len(qsos_before) == 1
        assert len(qsos_after) == 0

    def test_edit_qso(self):
        """Check that a qso's fields can be successfully edited."""
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )

        c.execute("SELECT * FROM test")
        qso_before = c.fetchall()[0]

        self.log.edit_qso(1, "CALL", "TEST456")
        self.log.edit_qso(1, "FREQ", "145.450")

        c.execute("SELECT * FROM test")
        qso_after = c.fetchall()[0]

        assert qso_before["CALL"] == "TEST123"
        assert qso_after["CALL"] == "TEST456"
        assert qso_before["FREQ"] == "145.500"
        assert qso_after["FREQ"] == "145.450"

    def test_get_qso_by_index(self):
        """Check that a qso can be retrieved using its index."""
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )

        qso = self.log.get_qso_by_index(1)
        print("Contents of retrieved qso: ", qso)
        for field_name in list(qso.keys()):
            if field_name.upper() == "ID":
                continue
            else:
                assert (
                    qso[field_name.upper()] == self.fields_and_data[field_name.upper()]
                )
        assert len(qso) == len(self.fields_and_data) + 1

    def test_qsos(self):
        """Check that all qsos in a log can be successfully retrieved."""
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        # Add the same qso twice
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )

        qsos = self.log.qsos
        print("Contents of all retrieved qsos: ", qsos)
        assert len(qsos) == 2  # There should be 2 qsos
        for field_name in self.field_names:
            assert qsos[0][field_name] == self.fields_and_data[field_name]
            assert qsos[1][field_name] == self.fields_and_data[field_name]

    def test_qso_count(self):
        """Check that the total number of qsos in a log is calculated correctly."""
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        # Add the same qso twice
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )
        c.execute(
            query,
            (
                self.fields_and_data["CALL"],
                self.fields_and_data["QSO_DATE"],
                self.fields_and_data["TIME_ON"],
                self.fields_and_data["FREQ"],
                self.fields_and_data["BAND"],
                self.fields_and_data["MODE"],
                self.fields_and_data["RST_SENT"],
                self.fields_and_data["RST_RCVD"],
            ),
        )

        qso_count = self.log.qso_count
        print("Number of qsos in the log: ", qso_count)
        assert qso_count == 2  # There should be 2 qsos

    def test_get_duplicates(self):
        """Insert n qsos, n-1 of which are duplicates, and check that the duplicates are successfully identified."""
        query = "INSERT INTO test VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)"
        c = self.connection.cursor()
        n = 5  # The total number of qsos to insert.
        for i in range(0, n):
            c.execute(
                query,
                (
                    self.fields_and_data["CALL"],
                    self.fields_and_data["QSO_DATE"],
                    self.fields_and_data["TIME_ON"],
                    self.fields_and_data["FREQ"],
                    self.fields_and_data["BAND"],
                    self.fields_and_data["MODE"],
                    self.fields_and_data["RST_SENT"],
                    self.fields_and_data["RST_RCVD"],
                ),
            )
        assert len(self.log.get_duplicates()) == n - 1  # Expecting n-1 duplicates.

    def test_remove_duplicates(self):
        """Insert n qsos, n-1 of which are duplicates, and check that the duplicates are successfully removed."""
        n = 5  # The total number of qsos to insert.
        for i in range(0, n):
            self.log.add_qso(self.fields_and_data)
        (
            number_of_duplicates,
            number_of_duplicates_removed,
        ) = self.log.remove_duplicates()
        print("Number of duplicates: %d" % number_of_duplicates)
        print("Number of duplicates removed: %d" % number_of_duplicates_removed)
        assert number_of_duplicates == number_of_duplicates_removed
        assert number_of_duplicates == 4
        assert self.log.qso_count == 1

    def test_rename(self):
        """Check that a log can be successfully renamed."""
        old_name = "test"
        new_name = "hello"
        success = self.log.rename(new_name)
        assert success
        with self.connection:
            c = self.connection.cursor()
            c.execute(
                "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?)", [old_name]
            )
            exists = c.fetchone()
            assert exists[0] == 0  # Old log name should no longer exist.
            c.execute(
                "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?)", [new_name]
            )
            exists = c.fetchone()
            assert exists[0] == 1  # New log name should now exist.
        assert self.log.name == new_name


if __name__ == "__main__":
    unittest.main()
