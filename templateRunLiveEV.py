import sys  # We need sys so that we can pass argv to QApplication
import os  # For listing filepath methods

sys.path.append("/opt/mantidnightly/bin")

from mantid.simpleapi import *

self.instrument = "{instrument}"
self.seconds = {seconds}
self.script = "{outputDirectory}"+"/liveEV.py"
StartLiveData(Instrument=self.instrument, UpdateEvery = self.seconds, PreserveEvents=True,
                  AccumulationMethod = "Add", OutputWorkspace="live", PostProcessingScriptFilename=self.script)
