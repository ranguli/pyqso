from loguru import logger
import configparser
from os.path import expanduser

class FormDialog:

    def __init__(self, application, log, db, index=None):
        self.application = application
        self.builder = self.application.builder

        self.db_table = db[log.name]

        # Check if a configuration file is present, since we might need it to set up the rest of the dialog.
        self.config = configparser.ConfigParser()
        self.have_config = self.config.read(expanduser("~/.config/pyqso/preferences.ini")) != []

    def get_form(self):
        form_data = {}

        for field in self.db_table.columns:
            try:
                form_data.update({field: self.get_form_field_text(field)})
            except ValueError as e:
                logger.exception(e)

        logger.debug(f"Form data returned by QSODialog.get_form() is '{form_data}'")
        return form_data

    def get_form_field(self, form_field):
        try:
            value = self.builder.get_object(f"{form_field}_entry")
            logger.debug(f"Form data returned by QSODialog.get_form_field({form_field}) is '{value}'")
            return value
        except AttributeError as e:
            logger.exception(f"Form field '{form_field}' could not be found: '{e}'")

    def get_form_field_text(self, form_field):
        logger.debug(f"QSODialog.get_form_field_text() received parameter '{form_field}'")

        try:
            value = self.builder.get_object(f"{form_field}_entry").get_text()
            logger.debug(f"QSODialog.get_form_field_text() returned '{value}'")
            return value
        except AttributeError:
            pass

        try:
            value = self.builder.get_object(f"{form_field}_combo").get_active_text()
            logger.debug(f"QSODialog.get_form_field_text() returned {value})")
            return value
        except AttributeError:
            pass

        try:
            field = self.builder.get_object(f"{form_field}_textview").get_buffer()
            (start, end) = field.get_bounds()
            value = field.get_text(start, end, True)
            logger.debug(f"QSODialog.get_form_field_text() returned {value})")
            return value
        except AttributeError:
            pass

        raise KeyError(f"Form field '{form_field}' could not be found.")

    def set_form_field(self, form_field_name, value):
        logger.debug(f"Trying to find form field {form_field_name}")
        form_field_object = self.get_form_field(form_field_name)
        logger.debug(f"Got {form_field_object}")

        try:
            return form_field_object.set_text(value)
        except AttributeError:
            pass

        try:
            return form_field_object.set_activetext(value)
        except AttributeError:
            pass

        try:
            field = form_field_object.set_buffer(value)
            (start, end) = field.get_bounds()
            return field.get_text(start, end, True)
        except AttributeError:
            pass
