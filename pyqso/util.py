import pathlib


def get_glade_path():
    glade_file_path = str(
        pathlib.Path(__file__).parent.resolve() / "ui" / "res" / "pyqso.glade"
    )
    return glade_file_path
