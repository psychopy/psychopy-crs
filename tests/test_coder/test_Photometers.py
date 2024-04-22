from psychopy import hardware, plugins
from psychopy_crs.colorcal import ColorCAL
from psychopy_crs.optical import OptiCAL


plugins.activatePlugins()


def test_getPhotometers():
    """
    Test that CRS photometers appear in getAllPhotometers once plugins are activated
    """
    # get all photometers
    photoms = hardware.getAllPhotometers()
    # make sure classes are present
    assert ColorCAL in photoms
    assert OptiCAL in photoms