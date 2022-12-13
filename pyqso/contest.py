CONTESTS = [
    "",
    "AP-SPRINT",
    "ARRL-10",
    "ARRL-160",
    "ARRL-222",
    "ARRL-DX-CW",
    "ARRL-DX-SSB",
    "ARRL-RR-PH",
    "ARRL-RR-DIG",
    "ARRL-RR-CW",
    "ARRL-SCR",
    "ARRL-SS-CW",
    "ARRL-SS-SSB",
    "ARRL-UHF-AUG",
    "ARRL-VHF-JAN",
    "ARRL-VHF-JUN",
    "ARRL-VHF-SEP",
    "ARRL-RTTY",
    "BARTG-RTTY",
    "CQ-160-CW",
    "CQ-160-SSB",
    "CQ-WPX-CW",
    "CQ-WPX-RTTY",
    "CQ-WPX-SSB",
    "CQ-VHF",
    "CQ-WW-CW",
    "CQ-WW-RTTY",
    "CQ-WW-SSB",
    "DARC-WAEDC-CW",
    "DARC-WAEDC-RTTY",
    "DARC-WAEDC-SSB",
    "DL-DX-RTTY",
    "DRCG-WW-RTTY",
    "FCG-FQP",
    "IARU-HF",
    "JIDX-CW",
    "JIDX-SSB",
    "NAQP-CW",
    "NAQP-SSB",
    "NA-SPRINT-CW",
    "NA-SPRINT-SSB",
    "NCCC-CQP",
    "NEQP",
    "OCEANIA-DX-CW",
    "OCEANIA-DX-SSB",
    "RDXC",
    "RSGB-IOTA",
    "SAC-CW",
    "SAC-SSB",
    "STEW-PERRY",
    "TARA-RTTY",
]



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
