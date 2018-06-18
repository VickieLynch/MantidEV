import sys
import time

sys.path.insert(0,"/opt/mantidnightly/bin")

from mantid.simpleapi import *

instrument = "{instrument}"
seconds = {seconds}
script = "{outputDirectory}"+"/MantidEV.py"
StartLiveData(Instrument=instrument, UpdateEvery = seconds, PreserveEvents=True,
                  AccumulationMethod = "Add", AccumulationWorkspace="tmp",
                  OutputWorkspace="output", PostProcessingScriptFilename=script)
print('Type Ctrl-C to cancel')
try:
    while True:
        time.sleep(1)
finally:
    AlgorithmManager.newestInstanceOf("MonitorLiveData").cancel()

