try:
    from psychopy.experiment.monitor import BasePhotometerDeviceBackend
except ModuleNotFoundError:
    BasePhotometerDeviceBackend = object

class SpectroCALDeviceBackend(BasePhotometerDeviceBackend):
    backendLabel = "SpectroCAL"
    deviceClass = "psychopy_crs.hardware.spectrocal.SpectroCALDevice"

    def getParams(self):
        return [], {}

    def writeDeviceCode(self, buff):
        # write core code
        BasePhotometerDeviceBackend.writeBaseDeviceCode(self, buff, close=True)
