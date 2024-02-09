from file_io.metadata import Metadata


class Report:
    def __init__(self, has_errors : bool, has_warnings : bool,report_str : str):
        self.report_str = report_str
        self.has_errors = has_errors
        self.has_warnings = has_warnings

    def __str__(self):
        return self.report_str


def get_report(filepath : str, metadata : Metadata, deg_over_intensity : list):
    report_str = f'Successfully processed file {filepath}'
    has_errors = True
    has_warnings = True

    error_start = '- Errors:'
    error_str = error_start
    if metadata.primary_wavelength_angstrom is None:
        error_str += "\nPrimary wavelength missing!"

    if len(deg_over_intensity) == 0:
        error_str += "\nNo data found. Degree over intensity is empty!"

    elif len(deg_over_intensity) < 10:
        error_str += "\nData is too short. Less than 10 entries!"

    if error_str == error_start:
        error_str = f'\nNo errors found: Wavelength and data successfully parsed'
        has_errors = False
    report_str += error_str

    warning_start = '- Warnings:'
    warning_str = warning_start
    if metadata.secondary_wavelength_angstrom is None:
        warning_str += "\nNo secondary wavelength found"
    if metadata.anode_material is None:
        warning_str += "\nNo anode material found"
    if metadata.measurement_datetime is None:
        warning_str += "\nNo measurement datetime found"

    if warning_str == warning_start:
        warning_str = f'\nNo warnings found: All metadata was successfully parsed'
        has_warnings = False

    report_str += warning_str

    return Report(report_str=report_str, has_errors=has_errors, has_warnings=has_warnings)
