import sys  # We need sys so that we can pass argv to QApplication
import os  # For listing filepath methods

sys.path.append("/opt/mantidnightly/bin")

from mantid.simpleapi import *

instrument = "{instrument}"
seconds = {seconds}
script = "{outputDirectory}"+"/MantidEV.py"
StartLiveData(Instrument=instrument, UpdateEvery = seconds, PreserveEvents=True,
                  AccumulationMethod = "Add", AccumulationWorkspace="tmp", OutputWorkspace="live", PostProcessingScriptFilename=script)
