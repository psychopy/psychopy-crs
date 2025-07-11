from psychopy import hardware
from psychopy_crs import optical


def test_getPhotometers():
    """
    Test that CRS photometers appear in legacy getAllPhotometers output
    """
    # get all photometers
    photoms = hardware.getAllPhotometers()
    # make sure class is present
    assert optical.OptiCAL in photoms.values()
