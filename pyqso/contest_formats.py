class ContestLogTemplate:
    @property
    def headers():
        return


class ARRL10(ContestLogTemplate):
    def __init__(self):
        pass

    def convert_qso(row):
        """
        Return a Cabrillo record in the correct format for the ARRL 10 meter
        contest
        """

        # self.qso_format

        pass

    @property
    def qso_format(self):
        return ["date", "time", "call", "rst_rcvd", "qth_serial"]

    @property
    def headers(self):
        return {
            "CONTEST": "ARRL-10",
            "CATEGORY-ASSISTED": "{{category_assisted}}",
            "CATEGORY-BAND": "10M",
            "CATEGORY-MODE": "{{category_mode}}",
            "CATEGORY-OPERATOR": "{{category_operator}}",
            "CATEGORY-POWER": "{{category_power}}",
            "CATEGORY-STATION": "{{category_station}}",
            "CATEGORY-TRANSMITTER": "{{category_transmitter}}",
        }
