import time
from psychopy import logging, clock
from psychopy.hardware.serialdevice import SerialDevice
from psychopy.hardware.photometer import BasePhotometerDevice, PhotometerResponse
from psychopy.tools import systemtools
import re


class SpectroCALResponse(PhotometerResponse):
    fields = PhotometerResponse.fields + ["spd", "chrom"]
    def __init__(self, t, value, spd, chrom, device=None):
        PhotometerResponse.__init__(
            self,
            t=t,
            value=value,
            device=device
        )
        # store spd
        self.spd = spd
        self.chrom = chrom


class SpectroCALDevice(BasePhotometerDevice):

    responseClass = SpectroCALResponse

    def __init__(
        self,
        port
    ):
        # initialize
        BasePhotometerDevice.__init__(self)
        # create serial device
        self.com = SerialDevice(
            port=port,
            baudrate=921600,
            byteSize=8,
            parity="N",
            stopBits=1,
            eol=b"\r",
            pauseDuration=0.1
        )
        # store port
        self.port = port
        # start a clock
        self.clock = clock.Clock()
    
    def syncClock(self, other):
        """
        Synchronise this device's clock with another clock.

        Parameters
        ----------
        other : psychopy.clock.Clock
            Clock to sync with
        """
        self.clock._timeAtLastReset = other._timeAtLastReset
        self.clock._epochTimeAtLastReset = other._epochTimeAtLastReset
    
    def laserOn(self):
        """
        Turn on the SpectroCAL's laser.

        Returns
        =======
        bool
            True if completed successfully
        """
        self.com.sendMessage("*CONTR:LASER 1")

        return self.com.awaitResponse() == chr(6)

    def laserOff(self):
        """
        Turn off the SpectroCAL's laser.

        Returns
        =======
        bool
            True if completed successfully
        """
        self.com.sendMessage("*CONTR:LASER 0")

        return self.com.awaitResponse() == chr(6)
    
    def setRefreshRate(self, frameRate=None):
        """
        Set the monitor refresh rate to sync to

        Parameters
        ----------
        frameRate : int or None
            Monitor refresh rate (frames per second) to sync to, use None for unsynced.

        Returns
        -------
        bool
            True if completed successfully
        """
        # set
        if frameRate is None:
            # set to unsynced mode
            self.com.sendMessage("*CONF:CYCMOD 0");
        else:
            # set to synced mode
            self.com.sendMessage("*CONF:CYCMOD 1");
            # set cycle time (in us)
            self.com.sendMessage(f"*CONF:CYCTIM {1000000/frameRate}");
        # should return 6
        return self.com.awaitResponse() == chr(6)

    def getRefreshRate(self):
        """
        Determine the refresh rate SpectroCAL takes measurements at

        Returns
        -------
        int
            Measured refresh rate (or None if not available)
        """
        # set to synced measurement mode
        self.com.sendMessage("*CONF:CYCMOD 1")
        err = self.com.awaitResponse()
        assert err == chr(6), f"Failed to set SpectroCAL to synchronized measuring mode. Error: {err}"
        # measure cycle time
        self.com.sendMessage("*CONTR:CYCTIM 200 4000")
        resp = self.com.awaitResponse(multiline=True)
        assert resp and resp[0] == chr(6), f"Failed to measure cycle time. Device sent: {err}"
        # get rate
        if len(resp) > 1:
            return 1000 / int(err[1])

    def setExposureAutoAdaption(self, value=True):
        """
        Tell the device whether to adapt automatically to exposure

        Parameters
        ----------
        value : bool
            Whether to adapt automatically to exposure
        
        Returns
        -------
        bool
            True if completed successfully
        """
        if value:
            self.com.sendMessage("*CONF:EXPO 1")
        else:
            self.com.sendMessage("*CONF:EXPO 0")
        # should return 6
        return self.com.awaitResponse() == chr(6)
    
    def getWavelengthRange(self):
        """
        Determine the wavelength range that SpectroCAL takes measurements across

        Returns
        -------
        int
            Start of predefined wavelength range
        int
            End of predefined wavelength range
        """
        # regex to find value without header
        RE_VALUE_ONLY = re.compile(r":\t(\d+)\r")
        # request start
        self.com.sendMessage("*PARA:WAVBEG?")
        # get without header
        start = RE_VALUE_ONLY.search(
            self.com.awaitResponse()
        )
        if start:
            start = int(start.group(1))
        # request stop
        self.com.sendMessage("*PARA:WAVEND?")
        # get without header
        stop = RE_VALUE_ONLY.search(
            self.com.awaitResponse()
        )
        if stop:
            stop = int(stop.group(1))

        return start, stop

    def setWavelengthRange(self, start, stop, step=1):
        """
        Set the wavelength range that SpectroCAL takes measurements across

        Parameters
        ----------
        start
            Start of predefined wavelength range
        stop
            End of predefined wavelength range
        step
            Sample step size in nm (can be 1 or 5)
        """
        self.com.sendMessage(f"*CONF:WRAN {start} {stop} {step}")
        # should return 6
        return self.com.awaitResponse() == chr(6)
    
    def setRadiometricSpectra(self, value=6):
        """
        Set the radiometric spectra in nm

        Parameters
        ----------
        value : int
            Radiometric spectra in nm / value 
        """
        self.com.sendMessage(f"*CONF:FUNC {value}")
        # should return 6
        return self.com.awaitResponse() == chr(6)
        
    def dispatchMessages(self, spd=False):
        """
        When called, dispatch a single reading.

        Parameters
        ----------
        spd : bool
            If True, request the full SPD mapping (this could take up to 240s)
        """
        # make sure auto adaptation is on
        self.setExposureAutoAdaption(True)
        # setup a timeout
        timeout = clock.CountdownTimer(240)
        # tell it to start
        self.com.sendMessage("*INIT")
        self.com.pause()
        logging.debug(
            "Measuring Spectral Power Distribution, will timeout after 240s if insufficient signal."
        )
        # wait while it processes
        finished = False
        while not finished:
            # wait until device sends a start flag
            resp = self.com.awaitResponse(multiline=False, timeout=timeout.getTime())
            # if we get a start flag, wait for a stop flag
            if resp == chr(6) and timeout.getTime() > 0:
                resp = self.com.awaitResponse(multiline=False, timeout=timeout.getTime())
                if resp == chr(7):
                    finished = True
            # if we get a start and stop in the same message, init has finished
            if resp == chr(6) + chr(7):
                finished = True
        # if we timed out, init most likely failed
        if timeout.getTime() < 0:
            raise TimeoutError("Photometer timed out due to insufficient signal")
        if spd:
            # get SPD
            self.com.sendMessage("*FETCH:SPRAD 7")
            self.com.pause()
            spd = self.com.awaitResponse(multiline=True, timeout=10)
        else:
            spd = None
        # get luminance
        self.com.sendMessage("*FETCH:PHOTO 7")
        self.com.pause()
        lum = self.com.awaitResponse(multiline=False)
        # get CIE xy chromaticity coordinates
        self.com.sendMessage("*FETCH:CHROMXY 7")
        self.com.pause()
        chromxy = self.com.awaitResponse(multiline=True)
        if chromxy is None:
            chromxy = []
        # get CIE u'v' chromaticity coordinates
        self.com.sendMessage("*FETCH:CHROMUV 7")
        self.com.pause()
        chromuv = self.com.awaitResponse(multiline=True)
        if chromuv is None:
            chromuv = []

        # dispatch
        self.receiveMessage(
            self.parseMessage({
                'spd': spd,
                'lum': lum,
                'chrom': chromxy + chromuv
            })
        )

    def parseMessage(self, message):
        # parse spd
        if message['spd'] is not None:
            spd = {}
            for reading in message['spd']:
                # delineate
                try:
                    key, val = delineateTabReading(reading)
                except InvalidReadingError:
                    continue
                # store
                spd[key] = val
        else:
            spd = None
        # parse luminance
        lum = None
        if ":\t" in message['lum']:
            lum = float(message['lum'].split(":\t")[1])

        # parse CIE chromaticity coordinates
        chrom = {
            'x': None,
            'y': None,
            'u\'': None,
            'v\'': None,
        }
        for reading in message['chrom']:
            # match message start to key in output
            for key, ident in (
                ("x", "Chrom_x:\t"),
                ("y", "Chrom_y:\t"),
                ("u'", "Chrom_u':\t"),
                ("v'", "Chrom_v':\t"),
            ):
                # if reading matches expected message start...
                if reading.startswith(ident):
                    # convert the rest to a float and store against key
                    try:
                        chrom[key] = float(reading.replace(ident, ""))
                    except:
                        # skip any that fail
                        continue
        
        return SpectroCALDevice.responseClass(
            t=self.clock.getTime(),
            value=lum,
            spd=spd,
            chrom=chrom,
            device=self
        )

    def isSameDevice(self, other):
        if isinstance(other, SpectroCALDevice):
            return other.com.isSameDevice(self.com)
    
    @staticmethod
    def getAvailableDevices():
        import serial.tools.list_ports

        profiles = []

        # iterate through serial devices via pyserial
        for device in serial.tools.list_ports.comports():
            # filter only for those which look like a spectrocal
            if device.vid in (861, 1027) and device.pid in (1000, 1001, 1002, 1003, 1004, 24577):
                # construct profile
                profiles.append({
                    'deviceName': f"SpectroCAL@{device.device}",
                    'deviceClass': "psychopy_crs.hardware.spectrocal.SpectroCALDevice",
                    'port': device.device
                })
        
        return profiles


class InvalidReadingError(ValueError):
    def __init__(self, reading, err):
        ValueError.__init__(self, f"Invalid reading '{reading}': {err}")
        

def delineateTabReading(reading):
    """
    Parse a tab-delineated reading into a key:value pair.

    Parameters
    ----------
    reading : str
        Reading, with a tab delineator

    Returns
    -------
    int
        Key
    float
        Value
    """
    # reading must contain a tab
    if "\t" not in reading:
        raise InvalidReadingError(reading, "Is not tab delineated")
    # get key and value
    key, val = reading.split("\t", 1)
    # reading must contain data
    if not key or not val:
        raise InvalidReadingError(reading, "Is blank")
    # key must be a valid integer
    try:
        key = int(key)
    except:
        raise InvalidReadingError(reading, "Key could not be converted to int")
    # value must be a valid float
    try:
        val = float(val)
    except:
        raise InvalidReadingError(reading, "Value could not be converted to float")
    
    return key, val