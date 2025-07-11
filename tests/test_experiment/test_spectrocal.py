import pytest


def test_spectrocalClassDetected():
    """
    Check that the Builder element for SpectroCal is detected (so it appears in Monitor Center)
    """
    try:
        from psychopy.experiment.monitor import BasePhotometerDeviceBackend
    except ModuleNotFoundError:
        pytest.skip()
    # get all known subclasses of BasePhotometerBackend
    knownClasses = BasePhotometerDeviceBackend.__subclasses__()
    # make sure SpectroCALDeviceBackend is in there
    from psychopy_crs.experiment.spectrocal import SpectroCALDeviceBackend
    assert SpectroCALDeviceBackend in knownClasses
