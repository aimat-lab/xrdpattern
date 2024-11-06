from enum import Enum

class XrdAnode(Enum):
    Cu = "Cu"
    Mo = "Mo"
    Cr = "Cr"
    Fe = "Fe"
    Co = "Co"
    Ag = "Ag"

    def get_wavelengths(self) -> (float, float):
        MATERiAL_TO_WAVELENGTHS = {
            "Cu": (1.54439, 1.54056),
            "Mo": (0.71359, 0.70930),
            "Cr": (2.29361, 2.28970),
            "Fe": (1.93998, 1.93604),
            "Co": (1.79285, 1.78896),
            "Ag": (0.563813, 0.559421),
        }
        return MATERiAL_TO_WAVELENGTHS[self.value]

    @staticmethod
    def compute_ratio():
        return 0.5

