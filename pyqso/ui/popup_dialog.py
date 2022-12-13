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


class PopupDialog:
    def __init__(self, parent, message):
        self.parent = parent
        self.message = message

    def error(self):
        self.buttons = Gtk.ButtonsType.OK
        self.title = "Error"
        self.msgtype = Gtk.MessageType.ERROR

        return self.show()

    def info(self):
        self.buttons = Gtk.ButtonsType.OK
        self.title = "Info"
        self.msgtype = Gtk.MessageType.INFO

        return self.show()

    def question(self):
        self.buttons = Gtk.ButtonsType.YES_NO
        self.title = "Question"
        self.msgtype = Gtk.MessageType.QUESTION

        return self.show()

    def show(self):
        """
        Instantiate and present a dialog to the user.

        :arg parent: The Gtk parent window/dialog.
        :arg Gtk.MessageType msgtype: The type of message to present to the user (e.g. a question, or error message).
        :arg str message: The message to display in the dialog.
        :arg str title: The title to display at the top of the dialog.
        :returns: The response from the user, based on which button they pushed.
        :rtype: Gtk.ResponseType
        """
        dialog = Gtk.MessageDialog(
            self.parent,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            self.msgtype,
            self.buttons,
            self.message,
            self.title,
        )
        response = dialog.run()
        dialog.destroy()
        return response
