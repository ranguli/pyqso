import pathlib

from pyqso import adif

def get_glade_path():
    glade_file_path = str(
        pathlib.Path(__file__).parent.resolve() / "ui" / "res" / "pyqso.glade"
    )
    return glade_file_path

def guess_frequency_band(frequency):
    """ Takes a frequency (such as 14.320) and returns the band name (such as 20m) """
    for i in range(1, len(adif.BANDS)):
        if (
            frequency >= adif.BANDS_RANGES[i][0]
            and frequency <= adif.BANDS_RANGES[i][1]
        ):
            return i
