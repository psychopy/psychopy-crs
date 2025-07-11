from psychopy.experiment.monitor import BasePhotometerDeviceBackend


def test_spectrocalClassDetected():
    """
    Check that the Builder element for SpectroCal is detected (so it appears in Monitor Center)
    """
    # get all known subclasses of BasePhotometerBackend
    knownClasses = BasePhotometerDeviceBackend.__subclasses__()
    # make sure SpectroCALDeviceBackend is in there
    from psychopy_crs.experiment.spectrocal import SpectroCALDeviceBackend
    assert SpectroCALDeviceBackend in knownClasses
