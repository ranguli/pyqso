# Define the more user-friendly versions of the field names.

FIELD_NAMES_FRIENDLY = {
    "call": "Callsign",
    "date": "Date",
    "time": "Time",
    "freq": "Frequency (MHz)",
    "band": "Band",
    "mode": "Mode",
    "submode": "Submode",
    "prop_mode": "Propagation Mode",
    "tx_pwr": "TX Power (W)",
    "rst_sent": "RST Sent",
    "rst_rcvd": "RST Received",
    "qsl_sent": "QSL Sent",
    "qsl_rcvd": "QSL Received",
    "notes": "Notes",
    "name": "Name",
    "address": "Address",
    "state": "State",
    "country": "Country",
    "dxcc": "DXCC",
    "cqz": "CQ Zone",
    "ituz": "ITU Zone",
    "iota": "IOTA Designator",
    "gridsquare": "Grid Square",
    "sat_name": "Satellite Name",
    "sat_mode": "Satellite Mode",
}


class Data:


    @staticmethod
    def get_friendly_field_name(field_name):
        return FIELD_NAMES_FRIENDLY.get(field_name)

