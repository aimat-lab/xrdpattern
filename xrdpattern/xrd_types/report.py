from serialization import SerializableDataclass
from dataclasses import dataclass, field
from .metadata import Metadata

@dataclass
class Report(SerializableDataclass):
    filepath: str
    critical_errors: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def has_critical_error(self):
        return len(self.critical_errors) != 0

    def has_error(self):
        return len(self.errors) != 0

    def has_warning(self):
        return len(self.warnings) != 0

    def add_critical(self, msg : str):
        self.critical_errors.append(f'\n{msg}')

    def add_error(self, msg : str):
        self.errors.append(f'\n{msg}')

    def add_warning(self, msg : str):
        self.warnings.append(f'\n{msg}')

    def get_report_str(self):
        report_str = f'--- Successfully processed file ---'
        report_str += f'\nFilepath: {self.filepath}'
        report_str += f'\nNum critical errors: {len(self.critical_errors)}'
        report_str += f'\nNum errors: {len(self.errors)}'
        report_str += f'\nNum warnings: {len(self.warnings)}\n'

        if len(self.critical_errors) != 0:
            report_str += f'\nFound critical errors:'
            for crit_error_msg in self.critical_errors:
                report_str += crit_error_msg

        if len(self.errors) != 0:
            report_str += f'\nFound errors:'
            for error_msg in self.errors:
                report_str += error_msg

        if len(self.warnings) != 0:
            report_str += f'\nFound warnings:'
            for warning_msg in self.warnings:
                report_str += warning_msg
        report_str += '\n'
        return report_str

    def __str__(self):
        return self.get_report_str()


def get_report(filepath : str, metadata : Metadata, deg_over_intensity : dict):
    report = Report(filepath=filepath)

    if len(deg_over_intensity) == 0:
        report.add_critical('No data found. Degree over intensity is empty!')
    elif len(deg_over_intensity) < 10:
        report.add_critical('Data is too short. Less than 10 entries!')
    if metadata.primary_wavelength_angstrom is None:
        report.add_error('Primary wavelength missing!')

    if metadata.secondary_wavelength_angstrom is None:
        report.add_warning('No secondary wavelength found')
    if metadata.anode_material is None:
        report.add_warning('No anode material found')
    if metadata.measurement_datetime is None:
        report.add_warning('No measurement datetime found')


    return report


